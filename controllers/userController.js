	// TODO: replace by axios
const request = require('request')
const models = require('../models')
var jwtDecode = require('jwt-decode');
const jwt = require('njwt');
const crypto = require('crypto');
const managementApi = require('../middleware/managementApi');


// // Get all basemaps
exports.login = async (req, response) => {
  const {username, password} = req.body
  const crypto = require('crypto')
  const key = process.env.PASS_ENCRYPTION_KEY
  const algorithm = process.env.PASS_ENCRYPTION_ALGORITHM
  let cipher = crypto.createCipher(algorithm, key)
  let encrypted = cipher.update(password, 'utf8','hex')
  encrypted += cipher.final('hex')
  const user = await models.User.findOne({ where: { email: username, password: encrypted}})
  if (user){
    user.update({last_login: new Date()})
    var claims = { iss:'DFMS-API',
                  sub: user.id,
                  nickname: user.name,
                  email: user.email,
                  verified: user.email_Verified}
    var token = jwt.create(claims, process.env.AUTH0_CLIENT_SECRET)
    token.setExpiration(new Date().getTime() + 1000*60*60*10)
    return response.status(200).send({idToken: token.compact()})
  }
  else{
    return response.status(400).send('Username or password are incorrect')
  }
}

exports.forgotPassword = async (req, response) => {
  const { email } = req.body
  
}

exports.changePassword = async (req, response, next) => {
  const { current, password, passwordConfirmation } = req.body
  // We check the passwords are equal
  if (password !== passwordConfirmation) {
    return response.status(400).send({description: 'Passwords don\'t match'})
  }
  // We check the current one is correct
  try {
    const crypto = require('crypto')
    const key = process.env.PASS_ENCRYPTION_KEY
    const algorithm = process.env.PASS_ENCRYPTION_ALGORITHM
    const user = await models.User.findOne({ where: { id: req.user.sub }})
    let decipher = crypto.createDecipher(algorithm, key)
    let dec = decipher.update(user.password,'hex','utf8')
    dec += decipher.final('utf8')
    console.log(current, '\n', dec)
    if (current === dec){
      let cipher = crypto.createCipher(algorithm, key)
      let encrypted = cipher.update(password, 'utf8','hex')
      encrypted += cipher.final('hex')
      await user.update({password: encrypted})
      return response.status(200).send('Password successfully changed')
    }
    else {
      return response.status(400).send({description: 'The password you entered is incorrect'})
    }
  } catch (e) {
    next(e)
  }
}

exports.resetPassword = async (req, response, next) => {
  try{
    const {email, password} = req.body
    const crypto = require('crypto')
    const algorithm = process.env.PASS_ENCRYPTION_ALGORITHM
    const key = process.env.PASS_ENCRYPTION_KEY
    let cipher = crypto.createCipher(algorithm, key)
    let encrypted = cipher.update(password, 'utf8','hex')
    encrypted += cipher.final('hex')
    const user = await models.User.findOne({ where: { email: email }})
    if (user){
      await user.update({password: encrypted})
      const AWS = require('aws-sdk')
      const SESconfig = {
        apiVersion: '2010-12-01',
        accessKeyId: process.env.AWS_KEY,
        region: process.env.AWS_REGION
      }
      var emailParams = {
        Source: 'noreply@dfms.co.uk',
        Destination: {
          ToAddresses: [email]
        },
        Message: {
          Body: {
            Html: {
              Charset: "UTF-8",
              Data: 'Hi ' + user.name + '.<br>' + '<br>' +
                'Your password has been updated. Please use the following password to login to https://eval.dfms.co.uk .<br><br>' +
                'Your new password: ' + password + '<br><br>' +
                'If you have any queries, please do not hesitate to contact the DFMS Support team: support@dfms.co.uk .<br>' +
                '<br>Thank you.'
            }
          },
          Subject: {
            Charset: 'UTF-8',
            Data: 'Password reset'
          }
        }
      }
      new AWS.SES(SESconfig).sendEmail(emailParams).promise().then((res)=> {console.log(res);});
      response.sendStatus(200)
    }
  }
  catch (e) {
    next(e)
  }
}

exports.signup = async (req, response, next) => {
  // const { email, password, metadata, hash } = req.body
  try {
    const {email, metadata, password, organisation_name} = req.body
    const crypto = require('crypto')
    const hash = crypto.randomBytes(15).toString('hex')
    const AWS = require('aws-sdk')
    const algorithm = process.env.PASS_ENCRYPTION_ALGORITHM
    const key = process.env.PASS_ENCRYPTION_KEY
    let cipher = crypto.createCipher(algorithm, key)
    let encrypted = cipher.update(password, 'utf8','hex')
    encrypted += cipher.final('hex')
    console.log('encrypted pass: ', encrypted)
    let organisation
    let role
    role = req.body.role
    if (role !== "ADMIN" && role !== "SUPERADMIN"){
      role = "USER"
    }
    organisation = await models.Organisation.findOne({where: {name: organisation_name}})
    user = await models.User.findOne({where: {email: email}})
    if (!organisation){
      response.sendStatus(404)
    }
    if (user){
      return response.status(400).json('User already exists')
    } else {
      const SESconfig = {
        apiVersion: '2010-12-01',
        accessKeyId: process.env.AWS_KEY,
        region: process.env.AWS_REGION
      }
      var emailParams = {
        Source: 'noreply@dfms.co.uk',
        Destination: {
          ToAddresses: [email]
        },
        Message: {
          Body: {
            Html: {
              Charset: "UTF-8",
              Data: 'Hi ' + metadata.name + '.<br>' + '<br>' +
                'Thank you for your interest in the DFMS application. Please use the following details to login into the DFMS platform:<br>' +
                '<ul style="margin:0; margin-left: 25px; padding:0; align="left" type="disc">' +
                  '<li>https://eval.dfms.co.uk</li>' +
                  '<li>Username: '+ email + '</li>' +
                  '<li>Temporary password: ' + password + '</li>' +
                '</ul>' +
                'Please note you can change the temporary password from the setting menu.<br>' +
                'If you have any queries, please do not hesitate to contact the DFMS Support team: support@dfms.co.uk <br>' +
                '<br>Thank you.'
            }
          },
          Subject: {
            Charset: 'UTF-8',
            Data: 'Welcome to DFMS'
          }
        }
      }
      new AWS.SES(SESconfig).sendEmail(emailParams).promise().then((res)=> {console.log(res);});
      models.User.create({ id: hash+email, name: metadata.name, position: metadata.position, email, role, organisationId: organisation.id, password: encrypted, email_Verified: false })
    }
    return response.sendStatus(200);
  }
  catch(e) {
    next(e)
  }
}

exports.isAdmin = async (request, response, next) => {
  try {
    // check if the role is admin
    const user = await models.User.findOne({ where: { id: request.user.sub } })
    response.status(200).send(['ADMIN', 'SUPERADMIN'].includes(user.role))
  } catch (e) {
    next(e)
  }
}

exports.isSuperAdmin = async (request, response, next) => {
  try {
    // check if the role is super admin
    const user = await models.User.findOne({ where: { id: request.user.sub } })
    response.status(200).send(user.role === 'SUPERADMIN')
  } catch (e) {
    next(e)
  }
}

exports.getUser = async (request, response, next) => {
  try {
    let user = await models.User.findOne({ where: { id: request.user.sub } })
    response.status(200).send({
      email: user.email,
      name: user.name,
      position: user.position
    })
  } catch (e) {
    next(e)
  }
}

exports.updateUser = async (request, response, next) => {
  try {
    let user = await models.User.findOne({ where: { id: request.user.sub } })
    const { email, name, position } = request.body
    user = await user.update({ email, name, position })
    response.status(200).send('User saved')
  } catch (e) {
    next(e)
  }
}

exports.deleteUser = async (request, response, next) => {
  try {
    let user = await models.User.findOne({ where: { id: request.params.id } })
    // await managementApi.deleteUser(user.id)
    if (user){
      let resources = await models.Resource.findAll({where: {userId: user.id}})
      console.log(resources)
      for (var i = 0; i < resources.length; i++){
        console.log(resources[i])
        await resources[i].destroy()
      }
      await user.destroy()
      response.status(200).send('User deleted')
    } else {
      response.status(400).send('User does not exist')
    }
  } catch (e) {
    next(e)
  }
}
