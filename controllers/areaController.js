// Get Database models
const models = require('../models')

// // Get all user areas and areas shared with user
exports.getAreas = async (request, response, next) => {
  try {
    const users_areas = []
    const area_ids = []
    const results = await models.Area.findAll({ where: { userId: request.user.sub }, attributes: { exclude: ['userId'] }})
    for (var i = 0; i < results.length; i++)
    {
      var area = JSON.parse(JSON.stringify(results[i]))
      area['shared'] = false
      users_areas.push(area)
      area_ids.push(area.id)
    }
    const shared = await models.Shared.findAll({where: {User_Id: request.user.email}})
    if (shared){
      var shared_counter = 0
      while (shared_counter < shared.length) {
        widgets = await models.Widget.findAll({where: {dashboardId: shared[shared_counter].Dash_id}})
        var widget_counter = 0
        if (widgets){
          while (widget_counter < widgets.length){
            try {
              var id = widgets[widget_counter].properties.area.id
              } catch (e){
                var id = null
              }
              if (id){
                if (!area_ids.includes(id)){
                  shared_area = await models.Area.findOne({where:{id: id}})
                  if (shared_area){
                    var area = JSON.parse(JSON.stringify(shared_area))
                    area['shared'] = true
                    var d = await models.Dashboard.findOne({where: {id: shared[shared_counter].Dash_id}})
                    var userShared = await models.User.findOne({where: {id: d.userId}})
                    var org = await models.Organisation.findOne({where: {id: userShared.organisationId}})
                    var user = {}
                    user['name'] = userShared.name
                    user['organisation'] = org.name
                    area['user'] = user
                    area_ids.push(id)
                    users_areas.push(area)
                  }
                }
              }
              widget_counter++
            }
          }
          shared_counter++
        }
      }
    const dashboards = await models.Dashboard.findAll({where: {userId: request.user.sub}})
    // console.log(dashboards)
    for (var i = 0; i < dashboards.length; i++){
      dash = await models.Shared.findOne({where:{Dash_id: dashboards[i].id}})
      if (dash) {
          widgets = await models.Widget.findAll({where: {dashboardId: dash.Dash_id}})
          var widget_counter = 0
          // console.log(widgets)
          if (widgets){
            while (widget_counter < widgets.length){
              try {
                  var id = widgets[widget_counter].properties.area.id
                } catch (e){
                  var id = null
                }
                if (id){
                  if (!area_ids.includes(id)){
                    shared_area = await models.Area.findOne({where:{id: id}})
                    if (shared_area){
                      var area = JSON.parse(JSON.stringify(shared_area))
                      area['shared'] = true
                      var userShared = await models.User.findOne({where: {id: shared_area.userId}})
                      var org = await models.Organisation.findOne({where: {id: userShared.organisationId}})
                      var user = {}
                      user['userName'] = userShared.name
                      user['organisation'] = org.name
                      area['user'] = user
                      area_ids.push(id)
                      users_areas.push(area)
                    }
                  }
                }
                widget_counter++
              }
          }
      }
    }
    response.status(200).json(users_areas)
  } catch (e) {
    next(e)
  }
}

// Get single area by ID
exports.getAreaById = async (request, response, next) => {
  const id = parseInt(request.params.id)
  try {
    const results = await models.Area.findOne({ where: {id, userId: request.user.sub}, attributes: { exclude: ['userId'] }})
    response.status(200).json(results)
  } catch (e) {
    next(e)
  }
}

// Add a new area
exports.addArea = async (request, response, next) => {
  try {
    const { name, type, geom, idArea } = request.body
    const area = await models.Area.create({ name, type, geom, idArea, userId: request.user.sub })
    response.status(200).json(await models.Area.findOne({ where: {id: area.id, userId: request.user.sub}, attributes: { exclude: ['userId'] }}))
  } catch (e) {
    next(e)
  }
}

// // Update an existing area
exports.updateArea = async (request, response, next) => {
  try {
    const id = parseInt(request.params.id)
    const { name, type, geom, idArea } = request.body

    const area = await models.Area.findOne({ where: {id, userId: request.user.sub}, attributes: { exclude: ['userId'] }})
    const results = await area.update({ name, type, geom, idArea })

    response.status(200).send(results)
  } catch (e) {
    next(e)
  }
}

// // Delete a area
exports.deleteArea = async (request, response, next) => {
  try {
    const id = parseInt(request.params.id)
    // console.log(request.user)
    widgets = await models.Widget.findAll({where: {userId: request.user.sub}})
    // console.log(widgets)
    for (var i = 0; i < widgets.length; i++){
      if (widgets[i]['properties']['area'].id === id){
        await widgets[i].destroy()
      }
    }
    thresholds = await models.Threshold.findAll({where: {userId: request.user.sub, areaId: id}})
    // console.log(thresholds)
    await thresholds.destroy()
    // await models.Area.destroy({ where: {id, userId: request.user.sub} })
    response.status(200).send(`Resource deleted with ID: ${id}`)
  } catch (e) {
    next(e)
  }
}
