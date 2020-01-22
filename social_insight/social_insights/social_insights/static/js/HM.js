import React from 'react';
import ReactDOM from 'react-dom';
import 'script!jquery';
import 'script!foundation-sites/dist/foundation.min.js';
import 'script!timeago';
import TB from './TB.js';
import LP from './LP.js';
import Update from 'react-addons-update';
import { browserHistory, Router, Route, Link, withRouter , IndexRoute } from 'react-router'


require('foundation-sites/dist/foundation.min.css');
require('../css/foundation-icons/foundation-icons.css');
require('../css/home.css');
require('../images/pageloader.gif');

var sampleComments = require('./sampleComments');

var HM = React.createClass({
	getInitialState() {
	  	return {'feed':[],'loadingFeed':false};
	},
	getFeed(options,callBack){
		  	$('.se-pre-con').show();
		    $.ajax({
			  dataType: "json",
			  url: '/feed' ,
			  data: options,
			  beforeSend: () => setTimeout(() => this.setState({'loadingFeed':true}),0),
			  success: (feed) => {
				callBack(feed);
	            $('.se-pre-con').hide();
			  },
			  complete: () => this.setState({'loadingFeed':false})
			});	  	
	},
	render(){
		let options = {
				page : 1,
				sm_account_id: smAccountId,
				access_token: userInfo.access_token
			 };
	    return(
	      <div>
	     	 <img src="static/images/pageloader.gif" className="se-pre-con" style={{'display':'none'}} />
	          <TB/>	

		      {this.props.children}
	      </div>
	    );
	  }
});

module.exports = HM;
