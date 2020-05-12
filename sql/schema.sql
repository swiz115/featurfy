CREATE TABLE users(
  username VARCHAR(40) NOT NULL,
  access_token VARCHAR(500) NOT NULL,
  refresh_token VARCHAR(500) NOT NULL,
  token_expire INTEGER NOT NULL,
  PRIMARY KEY(username)
);
