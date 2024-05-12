# Trophycord
A Discord bot for Sony PlayStation Trophy notifications

## Getting your PSN API Key

To get started you need to obtain npsso <64 character code>. You need to follow the following steps

1. Login into your My PlayStation account.

2. In another tab, go to https://ca.account.sony.com/api/v1/ssocookie

3. If you are logged in you should see a text similar to this

```
{"npsso":"<64 character npsso code>"}
```

This npsso code will be used in the api for authentication purposes. The refresh token that is generated from npsso lasts about 2 months.

From: https://psnawp.readthedocs.io/en/latest/additional_resources/README.html#getting-started