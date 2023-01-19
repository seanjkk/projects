# SQL Mock Client Project

![database](images/database.jpg)

### Introduction

Writing a SQL query for a mock client request.

### Client's request

Client wants data on how salaries have changed at specific companies over time. They specifically want monthly timeseries data that shows how the average salary has changed for each company at the MSA level. The companies they are interested in are in the **client_company_list** table.

### Data

**positions** table
| user_id | position_id | company_id | title | mapped_role | msa | startdate | enddate |
|---|---|---|---|---|---|---|---|
| 1 | 123 | 3 | Software Engineer | Software Engineer | New York, NY | 2014-06 | 2020-08 |
| 1 | 234 | 5 | Software Engineer II | Software Engineer | San Francisco, CA | 2020-10 | NULL |
| 2 | 2435 | 1 | Real Estate Salesperson | Salesperson | New York, NY | 2018-06 | NULL |
| ... | ... | ... | ... | ... | ... | ... | ... |


**predicted_salaries** table
| company_id | mapped_role | msa | year | salary |
|---|---|---|---|---|
| 1 | Salesperson | New York, NY | 2014 | 90000 |
| 1 | Software Engineer | New York, NY | 2014 | 100000 |
| 2 | Salesperson | San Francisco, CA | 2010 | 80000 |
| ... | ... | ... | ... | ... |


**company_refs** table
| company_id | name |
|---|---|
| 1 | Google |
| 2 | Apple |
| 3 | Meta |
| ... | ... |

**client_company_list** table
| company_name |
|---|
| Meta |
| Apple |
| Netflix |
| ... |

### SQL Code
~~~sql
-- Creating a timeseries CTE with intervals of 1 month 
WITH timeseries AS (
    SELECT * 
    FROM generate_series(
        (SELECT MIN(startdate) FROM position_dedup), -- Minimum value
        (SELECT CASE WHEN 
            SUM(CASE WHEN enddate IS NULL THEN 1 ELSE 0 END) > 0 THEN CURRENT_DATE 
            ELSE MAX(enddate) END 
        FROM positions), -- Maximum value: if there is a NULL in enddate then the maximum value is the current date
        INTERVAL '1 month'
    ) AS year_month
),

-- Creating a CTE to get IDs of the companies that the client has requested
company_list AS (
    SELECT company_id, name 
    FROM company_refs 
    WHERE LOWER(name) IN (SELECT LOWER(company_name) FROM client_company_list)
),

-- Using previous CTEs, creating a CTE to count the number of people in each role based on company, location, and month, and cross joining with the timeseries CTE
role_temp AS (
    SELECT pd.company_id, 
        p.msa, 
        year_month, 
        p.mapped_role, 
        COUNT(p.mapped_role) AS role_count -- Counting the number of people in each role based on company, location, and month
    FROM company_list cl 
    LEFT JOIN positions p ON cl.company_id = p.company_id -- Left joining to only include requested companies
    CROSS JOIN timeseries -- Cross joining with the timeseries to multiply the rows for each month
    WHERE year_month BETWEEN startdate AND (CASE WHEN enddate IS NULL THEN CURRENT_DATE ELSE enddate END) 
    GROUP BY p.company_id, p.msa, year_month, mapped_role
),

-- Using the previous CTE, creating a CTE to calculate weighted salaries and counts for each role
salary_temp AS (
    SELECT t.company_id, 
        t.msa, 
        t.year_month, 
        t.mapped_role, 
        ps.salary * t.role_count AS total_salary, -- Will be used to calculate numerator value
        t.role_count AS total_count -- Will be used to calculate denomintor value
    FROM role_temp t 
    LEFT JOIN predicted_salaries ps ON t.company_id = ps.company_id
        AND t.msa = ps.msa 
        AND t.mapped_role = ps.mapped_role 
        AND EXTRACT(year FROM t.year_month) = ps.year 
    LEFT JOIN scaling_weights sw ON t.mapped_role = sw.mapped_role
),

-- Using the previous CTE, creating a CTE to sum the salary and count values based on company, msa, and month
monthly_sums_temp AS (
    SELECT company_id, 
        msa, 
        year_month, 
        SUM(total_salary) AS salary_sum, -- Calculating the numerator value
        SUM(total_count) AS count_sum -- Calculating the denominator value
    FROM salary_temp 
    GROUP BY company_id, msa, year_month
)

SELECT mst.company_id, 
    name, -- Adding the company name for client's ease of use 
    msa, 
    TO_CHAR(year_month, 'yyyy-mm'), -- Formatting to remove days
    salary_sum / count_sum AS avg_salary -- Calculating the average salary for each company, msa, and month
FROM monthly_sums_temp mst 
LEFT JOIN company_list cl ON mst.company_id = cl.company_id -- Joining with previous company CTE to add the company names
ORDER BY year_month ASC, company_id ASC; -- Ordering by year and month first, then company ID
~~~

