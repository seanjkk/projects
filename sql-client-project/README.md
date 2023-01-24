# SQL Mock Client Project

![database](images/database.jpg)

* **The Jupyter notebook can be opened [here](sql-project.ipynb)**

### Introduction

Writing an advanced SQL query for a client request using mock data.

### Client's request

The client wants data on how salaries have changed at specific companies over time. They specifically want monthly timeseries data that shows the average salary for each company at the MSA level. The companies they are interested in are in the **client_company_list** table.

### Data

Using [Mockaroo](https://www.mockaroo.com/), I created mock data for each table. The csv files can be found in the data folder.
* **positions** table: 1,000 rows
* **predicted_salaries** table: 420 rows
* **company_refs** table: 4 rows
* **client_company_list** table: 3 rows