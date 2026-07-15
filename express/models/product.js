const { Model, DataTypes } = require("sequelize");
const sequelize = require("../config/database");

class Product extends Model {
  static associate(models) {
    Product.belongsToMany(models.Order, {
      through: models.OrderProduct,
      foreignKey: "product_id",
      otherKey: "order_id",
    });

    Product.hasMany(models.OrderProduct, {
      foreignKey: "product_id",
      as: "OrderProducts",
    });
  }
}

Product.init(
  {
    name: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    price: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: false,
    },
    stock: {
      type: DataTypes.INTEGER,
      allowNull: false,
      defaultValue: 0,
    },
  },
  {
    sequelize,
    modelName: "Product",
    tableName: "products",
    timestamps: false,
  }
);

module.exports = Product;
