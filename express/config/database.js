const { Sequelize } = require("sequelize");

const sequelize = new Sequelize("performance_test", "test", "test", {
  host: "postgres",
  dialect: "postgres",
  logging: console.log,
  pool: {
    max: 40,
    min: 5,
    acquire: 30000,
    idle: 300000,
  },

  dialectOptions: {
    statement_timeout: 30000,
    idle_in_transaction_session_timeout: 30000,
  },
});

module.exports = sequelize;
