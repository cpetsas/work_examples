const express = require('express')
const router = express.Router()
const userController = require('../controllers/userController')
const checkJwt = require('../middleware/checkJwt');
const checkRights = require('../middleware/checkRights')

router.post('/login', userController.login)
router.post('/forgot_password', userController.forgotPassword)
router.post('/change_password', checkJwt, userController.changePassword)
router.post('/signup', checkJwt, checkRights.isSuperAdmin, userController.signup)
router.post('/resetPassword', checkJwt, checkRights.isSuperAdmin, userController.resetPassword)
// router.post('/signup', userController.signup)
router.get('/is_admin', checkJwt, userController.isAdmin)
router.get('/is_super_admin', checkJwt, userController.isSuperAdmin)
router.get('/', checkJwt, userController.getUser)
router.put('/', checkJwt, userController.updateUser)
router.delete('/:id', checkJwt, checkRights.isSuperAdmin, userController.deleteUser)

module.exports = router
