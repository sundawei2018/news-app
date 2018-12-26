var express = require('express');
var config = require('./config/config.json');
var cors = require('cors');
var path = require('path');
var passport = require('passport');
var bodyParser = require('body-parser');

// routers
var auth = require('./routes/auth');
var index = require('./routes/index');
var news = require('./routes/news');

var app = express();

app.use(bodyParser.json());


require('./models/main.js').connect(config.mongoDbUri);
var authCheckMiddleWare = require('./middleware/auth_checker');

app.use(passport.initialize());
var localSignupStrategy = require('./passport/signup_passport');
var localLoginStrategy = require('./passport/login_passport');
passport.use('local-signup', localSignupStrategy);
passport.use('local-login', localLoginStrategy);



// view engine setup
app.set('views', path.join(__dirname, '../client/build/'));
app.set('view engine', 'jade');
app.use('/static',
    express.static(path.join(__dirname, '../client/build/static/')));

// TODO: remove this after development is done
app.use(cors())

app.use('/', index);
app.use('/auth', auth);
app.use('/news', authCheckMiddleWare);
app.use('/news', news);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  res.status(404);
});

module.exports = app;
