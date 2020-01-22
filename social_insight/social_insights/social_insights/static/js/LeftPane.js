import React from 'react';
import PageSearch from './PageSearch.js';

import 'script!foundation-sites/dist/foundation.min.js';
import { browserHistory, Router, Route, Link, withRouter } from 'react-router'

var LeftPane = React.createClass({
    renderSmAccount(smAccount, id) {
        return (
            <li key={id} id={smAccount.id} className='paneItem' onClick={this.props.toggleOpen}>
                <Link to={`/smaccounts/${smAccount.id}/${smAccount.name.replace(/\s/g, '')}`} >{smAccount.name}</Link>
            </li>
        );
    },

    componentDidUpdate() {
        var url = window.location.href;
        var smdetail = url.split("/");
        var smId = smdetail[smdetail.length - 2];
        if ($('#pageList').find('.selectedItem').size() != 0) {
            var prevElement = $('#pageList').find('.selectedItem')[0]
            prevElement.className = "paneItem";
        }
        var currentElement = document.getElementById(smId);
        if (currentElement) {
            currentElement.className = "selectedItem";
        }
    },

    renderAccounts(smAccounts) {
        if (smAccounts.length > 0) {
            var accounts = this.props.smAccounts.map(this.renderSmAccount);
            return (
                <ul id='pageList'>
                        {accounts}
                    </ul>
            )
        } else {
            return (
                <ul className='followInfo'>
                    <div> 
                        <i className="fi-social-facebook size-100"/>
                        <p> Facebook pages you follow in Sosilee will be shown here </p>
                    </div>
                </ul>
            );
        }

    },

    render() {
        var smAccounts = this.props.smAccounts.map(this.renderSmAccount);
        var profileUrl = "https://www.facebook.com/" + this.props.user_id;
        var wH = $(window).height();
        $('#sideDiv').css({ height: wH });
        return (
            <div id="sideDiv" style={{'paddingTop':'10px','backgroundColor':'#E9EBEE'}}>
                    <Link to="/" className="menu-text menu-title hide-for-small "><strong>Sosilee</strong></Link> 
                    <span style={{'position':'relative','marginLeft':'48px'}}>
                        { !this.props.isDocked &&
                        <a onClick={this.props.toggleOpen} className="secondary button" href="#" >X</a>}
                    </span>
                    <div style={{'margin': '10px'}}>
                        <PageSearch selectionHandler={this.props.selectionHandler} toggleOpen={this.props.toggleOpen} />
                        <div className="row">
                            <div className="small-10 columns">
                                <p style={{'color':'#000'}}><a href={profileUrl} target="_blank" >{this.props.userName}</a></p>
                            </div>
                            <div className="small-2 columns">
                                <a href={'/logout'} title="Logout of Sosilee"><i className="fi-power"></i></a>
                            </div>
                        </div>
                        <h6 className='paneTitle'>Your Pages</h6>
                        <ul id='pageList'>
                            {smAccounts}
                        </ul>
                        <h6 className='paneTitle'>Analyze Your Pages</h6>
                        <ul id='pageList'>
                            <li className='paneItem'> Compare </li>
                        </ul>
                        <h6 className='paneTitle'>HELP</h6>
                        <ul id='pageList'>
                            <li className='paneItem'> 
                               <a href='/static/demo.gif'> Showcase </a>
                            </li>
                        </ul>
                    </div>
                </div>
        );
    }
});

module.exports = LeftPane;
