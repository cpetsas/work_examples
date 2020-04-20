const jwt = require('express-jwt');
const jwksRsa = require('jwks-rsa');
const models = require('../models')


// Create middleware for checking the JWT
// module.exports = jwt({
//   // Dynamically provide a signing key based on the kid in the header and the singing keys provided by the JWKS endpoint.
//   secret: jwksRsa.expressJwtSecret({
//     cache: true,
//     rateLimit: true,
//     jwksRequestsPerMinute: 5,
//     jwksUri: `https://${process.env.AUTH0_DOMAIN}/.well-known/jwks.json`
//   }),

//   // Validate the audience and the issuer.
//   audience: process.env.AUTH0_CLIENT_ID,
//   issuer: `https://${process.env.AUTH0_DOMAIN}/`,
//   algorithms: ['RS256']
// });

module.exports = checkJWT = async(request, response, next) => {
    try{
        var jwt = require('jsonwebtoken')
        var bearerHeader = request.headers["authorization"]
        if (typeof bearerHeader === 'undefined')
        {
            response.redirect('/')
        } else {
            var bearer = bearerHeader.split(" ")
            var bearerToken = bearer[1]
            jwt.verify(bearerToken, process.env.AUTH0_CLIENT_SECRET, function (err,decoded){
                if (err) {
                    return response.status(401).send(err)
                } else {
                    request.user = decoded
                    next()
                }
            })
        }
    }
    catch (e) {
        next(e)
    }
}
