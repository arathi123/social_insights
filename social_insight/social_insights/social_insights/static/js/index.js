import React from 'react';
import ReactDOM from 'react-dom';
import 'script!jquery';
import 'script!foundation-sites/dist/foundation.min.js';
import 'script!timeago';
import App from './app.js';
import Home from './home.js';
import LeftPane from './LeftPane.js';
import Content from './Content.js';
import FollowPage from './FollowPage.js';
import Update from 'react-addons-update';
import { browserHistory, Router, Route, Link, withRouter, IndexRoute } from 'react-router'

require('foundation-sites/dist/foundation.min.css');
require('../css/foundation-icons/foundation-icons.css');
require('../css/home.css');
require('../images/pageloader.gif');



ReactDOM.render((<Router history={browserHistory}>
    <Route path="/" component={App}>
    <IndexRoute component={Home}/>
	    <Route path="/smaccounts" component={LeftPane} />
	   	<Route path="/smaccounts/:id/:name" component={Content}/>
	   	<Route path="/follow/:id/:name" component={FollowPage}/>
    </Route>
  </Router>), document.getElementById('container'));
