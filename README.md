# Member ID Demo

![]('./docs/demo.png)

### About

Separately dockerized frontend, api, and cache to demonstrate generating and validating membership ids. Tasked with making this in 24-48 hours, having a local dev setup, and running in prod.

Frontend (directory: www) is a Vite typescript bundled single page application, with a simple widget using React + Styled Components. Gives feedback on generation/validation submissions.

Backend (directory: api) is an API using async Python with the Sanic framework. Instead of tracking member ids in a list/set, it initializes SQLite which is an in-memory SQL database. In the docker-compose/cluster config, you'll also find a redis instance which is being used to cache validation queries (expiration 10s).

### Setup

Easy to get started. Just 1) `docker-compose up` and then 2) when in the interface, hit the "Init/Reset Database Tables" button to create the `member_id` table in the SQLite in-memory database.
