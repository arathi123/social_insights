import React from 'react';
import { browserHistory, Router, Route, Link, withRouter } from 'react-router'
import LP from './LP.js';

var TB = React.createClass({
render(){
	return(
		<div>
			<div data-sticky-container>
				<div className="title-bar" data-responsive-toggle="example-menu" data-hide-for="medium">
				  <button className="menu-icon" type="button" data-toggle></button>
				  <div className="title-bar-title">Menu</div>
				</div>
				<div className="top-bar" id="example-menu" data-sticky data-options="marginTop:0;" style={{'width':'100%'}}>
				  <div className="small-12 column row">
					  <div className="top-bar-left">
					    <ul className="dropdown menu" data-dropdown-menu>
					      <li className="menu-text menu-title hide-for-small" >
					      <Link to="/">Sosilee</Link> </li>
					    </ul>
					  </div>
					  <div className="top-bar-right">
					    <ul className="menu">
					      <li><i className="step fi-magnifying-glass size-24"></i></li>
					      <li>
					       	  
					      </li>
					    </ul>
					  </div>
					</div>
				</div>
			</div>
			<LP/>
		</div>
		);
}
});

module.exports = TB;
