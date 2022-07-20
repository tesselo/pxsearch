const SSM = require("aws-sdk/clients/ssm");

module.exports.getParameters = async ({ resolveConfigurationProperty }) => {
  const region = await resolveConfigurationProperty(["provider", "region"]);
  const ssm = new SSM({ region });
  const policy = await ssm
    .getParameter({
      Name: "pxearch-secrets",
      WithDecryption: true,
    })
    .promise();
  const res = JSON.parse(policy.Parameter.Value);
  return {
    POSTGRES_DBNAME: res.POSTGRES_DBNAME,
    POSTGRES_HOST: res.POSTGRES_HOST,
    POSTGRES_PASS: res.POSTGRES_PASS,
    POSTGRES_USER: res.POSTGRES_USER,
    SENTRY_DSN: res.SENTRY_DSN,
  };
};