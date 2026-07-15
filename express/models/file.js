const { Model, DataTypes } = require("sequelize");
const sequelize = require("../config/database");

class File extends Model {}

File.init(
  {
    name: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    file_data: {
      type: DataTypes.BLOB("long"),
      allowNull: false,
    },
  },
  {
    sequelize,
    modelName: "File",
    tableName: "files",
    timestamps: false,
  }
);

module.exports = File;
