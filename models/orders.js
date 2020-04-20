const Sequelize = require('sequelize')

module.exports = (sequelize) => {
    class Orders extends Sequelize.Model {}
    Orders.init({
        id: {
            type: Sequelize.INTEGER,
            primaryKey: true,
            autoIncrement: true
        },
        status: {
            type: Sequelize.STRING,
            defaultValue: 'Order pending approval'
        },
        call_waiter: {
            type: Sequelize.BOOLEAN,
            defaultValue: 'f'
        },
        details: {
            type: Sequelize.JSON
        },
        request_bill: {
            type: Sequelize.BOOLEAN,
            defaultValue: 'f'
        },
        table_number: {
            type: Sequelize.INTEGER,
            unique: true
        }
    }, {
        sequelize,
        modelName: 'orders'});
    return Orders 
}