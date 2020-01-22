import React from 'react';
import PageSearch from './PageSearch';

import { browserHistory, Router, Route, Link, withRouter } from 'react-router'


var TopBar = React.createClass({
    handleClick() {
        if ('clickHandler' in this.props) {
            this.props.clickHandler()
        }
    },
    render() {
    	var imageUrl = "http://graph.facebook.com/" + this.props.user_id + "/picture?type=square";
        return (
            <div className="top-bar search-box">
              <div className="top-bar-title">
                <span data-responsive-toggle="responsive-menu" data-hide-for="medium">
                  <button style={{'marginTop':'-15px'}} className="menu-icon dark" type="button" data-toggle></button>
                </span>
                <Link to="/" className="menu-text menu-title hide-for-small "><strong>Sosilee</strong></Link> 
              </div>
              <div id="responsive-menu">
                <div className="top-bar-right">
                  <ul className="menu">
                    <li ><PageSearch selectionHandler={this.props.selectionHandler} /></li>
                    <li><a href="#" style={{'marginTop':'-15px','height':'65px'}}> <img src={imageUrl} /></a></li>
                    <li><a href={'/logout'}> Logout </a></li>
                  </ul>
                </div>
              </div>
            </div>
        );
    }
});

module.exports = TopBar;
