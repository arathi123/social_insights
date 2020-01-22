import React from 'react';
import 'script!foundation-sites/dist/foundation.min.js';
import { browserHistory, Router, Route, Link, withRouter } from 'react-router'

var LP = React.createClass({
	renderSmAccount(smAccount,id){
		return (
			/*TODO: set active item as highlighted when paneItem is clicked*/
			<li key={id} id={smAccount.id} className='paneItem' >
				<Link to={`/smaccounts/${smAccount.name.replace(/\s/g, '')}`}>{smAccount.name}</Link>
			</li>
		);
	},
	render(){
		var smAccountsa=[{'id':1,'name':'Airtel'},{'id':2,'name':'Dhoni'}];
		var smAccounts = smAccountsa.map(this.renderSmAccount);
		return (
			<div id='leftPanel' data-sticky-container className='large-3 columns' >
	          <div className='small-12 columns sticky' data-margin-top='6' data-sticky data-top-anchor='mainContent:top' style={{'height':'500px','marginRight':'10px'}}>
	            <h6 className='paneTitle'>Pages</h6>
	            <ul id='pageList'>
	            	{smAccounts}
	            </ul>	
	            <h6 className='paneTitle'>Analyze</h6>
	            <ul >
	            	<li className='paneItem'> Compare </li>
	            </ul>
	          </div>
	        </div>
			);
	}
});

module.exports = LP;