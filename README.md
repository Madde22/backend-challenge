# Madde22 Backend Challenge

Create a web application which can authenticate via JWT (Json Web Token), and serve an API to GET a list of breweries filtered by a query based on the openbrewerydb.

For the web serving part you could use either
- [Django](https://www.djangoproject.com/)
- [Strapi](https://strapi.io/)
- [NestJS](https://nestjs.com/)
- [NextJS](https://nextjs.org/)

Please include a middleware for logging on all requests

The login endpoint ( `POST /login` ) should return a signed JWT token on correct username/password.

The token should be signed and the signing secret should be provided via config.

The POST request's body should contain `{ username: string, password: string }`.

The following interface describes the user.

``` { id: string; username: string; password: string; } ```

The users should be stored inside a database. You can choose any db you like in your solution but the credentials should be provided via config.

The breweries endpoint ( `GET /breweries` ) should be guarded by a custom middleware.
The middleware should validate the token and check if the user exists in the database.

The datasource should be the OpenBreweryDB https://www.openbrewerydb.org/

Use the search API to fetch the data `https://api.openbrewerydb.org/breweries/search?query=pale`

The search param should be provided in the query params ( `GET /breweries?query=dog` )

If the user is not authenticated on `GET /breweries` return `401`.

If the user not provided a query param return data from `https://api.openbrewerydb.org/breweries`

If the user called any other then `POST /login` or `GET /breweries` return `404`.

Please use typescript if you choose Node.js.
