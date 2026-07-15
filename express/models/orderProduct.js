const { Model, DataTypes } = require("sequelize");
const sequelize = require("../config/database");

class OrderProduct extends Model {
  static associate(models) {
    OrderProduct.belongsTo(models.Order, {
      foreignKey: "order_id",
    });
    OrderProduct.belongsTo(models.Product, {
      foreignKey: "product_id",
    });
  }
}

OrderProduct.init(
  {
    order_id: {
      type: DataTypes.BIGINT,
      allowNull: false,
      primaryKey: true,
      references: {
        model: "Order",
        key: "id",
      },
    },
    product_id: {
      type: DataTypes.BIGINT,
      allowNull: false,
      primaryKey: true,
      references: {
        model: "Product",
        key: "id",
      },
    },
    quantity: {
      type: DataTypes.INTEGER,
      allowNull: false,
      defaultValue: 1,
    },
  },
  {
    sequelize,
    modelName: "OrderProduct",
    tableName: "order_products",
    timestamps: false,
  }
);

module.exports = OrderProduct;
