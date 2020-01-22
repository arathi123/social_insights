import React from 'react';
import ReactDOM from 'react-dom';
import 'script!jquery';
import 'script!foundation-sites/dist/foundation.min.js';
import 'script!timeago';
import Content from './Content.js';
import Update from 'react-addons-update';
import LeftPane from './LeftPane.js';
import PostContent from './PostContent.js';
import Sidebar from 'react-sidebar';

require('foundation-sites/dist/foundation.min.css');
require('../css/foundation-icons/foundation-icons.css');
require('../css/home.css');
require('../images/pageloader.gif');

var sampleComments = require('./sampleComments');

const styles = {
  sidebar: {
    width: 256,
    height: '100%',
    overflow: 'hidden'
  },
  content: {
    height: '100%',
  }
};
    </Route>
const styles = {

var App = React.createClass({

    getInitialState() {
        return {
            smAccounts: [],
            feed: [],
            loadingFeed: false,
            docked: false,
            open: false
        }
    },

    componentWillMount() {
        const mql = window.matchMedia(`(min-width: 800px)`);
        var wH = $(window).height();
        $('#sideDiv').css({height: wH});
        mql.addListener(this.mediaQueryChanged);
        this.setState({mql: mql, docked: mql.matches});
    },

    componentWillUnmount() {
        this.state.mql.removeListener(this.mediaQueryChanged);
    },

    onSetOpen(open) {
        this.setState({open: open});
    },

    mediaQueryChanged() {
        this.setState({docked: this.state.mql.matches});
    },

    toggleOpen(ev) {
        this.setState({open: !this.state.open});
        if (ev) {
            ev.preventDefault();
        }
    },

    getFeed(options, callback = null) {
        if (!this.state.loadingFeed) {
            $('.se-pre-con').show();
            $.ajax({
                dataType: "json",
                url: '/feed',
                data: options,
                beforeSend: () => setTimeout(() => this.setState({ 'loadingFeed': true }), 0),
                success: (feed) => {
                    if (callback == null) {
                        this.setState({ 'feedoptions': feed.data, feedOptions: { 'pagingID': feed.paging_id, 'sm_account_id': options.sm_account_id } });
                    } else {
                        callback(feed);
                    }
                    $('.se-pre-con').hide();
                },
                complete: () => setTimeout(() => this.setState({ 'loadingFeed': false }), 0)
            });
        } else {
            console.log("ajaxrequest already in progress", this.state.feedOptions);
        }
    },

    getSmAccounts() {
        $.ajax({
            dataType: "json",
            url: '/sm_accounts',options
            success: function(smAccounts) {
                if (smAccounts.sm_accounts.length > 0) {
                    this.setState({ 'smAccounts': smAccounts.sm_accounts });
                }
            }.bind(this)
        });
    },

    componentDidMount() {
        this.getSmAccounts();
        $(document).foundation();
    },


    handleFollowEvent(smAccount, type) {
        if (type === 'follow') {
            let newState = Update(this.state, {
                'smAccounts': {
                    $apply: (smAccounts) => {
                        smAccounts.push(smAccount);
                        return smAccounts;
                    }
                }
            });
            this.setState(newState);
        } else if (type === 'unfollow') {
            let newState = Update(this.state, {
                'smAccounts': {
                    $apply: (smAccounts) => {
                        var ix = -1;
                        for (var i = 0; i < smAccounts.length; i++) {
                            if (smAccounts[i].id == smAccount.id) {
                                ix = i;
                            }
                        }
                        if (ix > -1) {
                            smAccounts.splice(ix, 1);
                        }
                        return smAccounts;
                    }
                }
            });
            this.setState(newState);
        }
    },

    handleSelect(value) {
        this.setState({ selectedPage: value });
    },

    fetchNextPage() {
        if (!this.state.feedOptions.allPagesFetched) {
            let updateState = (feed) => {
                if (feed.data.length > 0) {
                    let newState = Update(this.state, {
                        'feed': { $push: feed.data },
                        'feedOptions': { 'pagingID': { $set: feed.paging_id } }
                    });
                    this.setState(newState);
                } else {
                    let newState = Update(this.state, {
                        'feedOptions': { 'allPagesFetched': { $set: true } }
                    });
                    this.setState(newState);
                }
            };
            let options = { pagingID: this.state.feedOptions.pagingID, sm_account_id: this.state.feedOptions.sm_account_id };
            this.getFeed(options, updateState);
        }
    },

    render() {
        var sidebarContent = <LeftPane smAccounts={this.state.smAccounts} user_id={userInfo.user_id} userName={userInfo.fb_user_name} selectionHandler={this.handleSelect} toggleOpen={this.toggleOpen} isDocked={this.state.docked} />;
        const sidebarProps = {
            sidebar: sidebarContent,
            docked: this.state.docked,
            open: this.state.open,
            onSetOpen: this.onSetOpen,
            shadow: false,
            touch: true,
            styles: styles
        };
        return (
            <div>
                <img src="/static/images/pageloader.gif" className="se-pre-con" style={{'display':'none'}} />
                <Sidebar {...sidebarProps}>
                    <span style={{'top':'10','position':'relative','marginLeft':'10'}}>
                        {!this.state.docked &&
                        <a onClick={this.toggleOpen} className="secondary button" href="#" >&#9776;</a>}
                    </span>
                    <div >
                        { this.props.children  && React.cloneElement(this.props.children, {
                            smAccounts:this.state.smAccounts ,
                            feed:this.state.feed,
                            getFeed:this.getFeed,
                            handleFollowEvent:this.handleFollowEvent,
                            selectedPage:this.state.selectedPage,
                            selectionHandler:this.handleSelect,
                            fetchNextPage:this.fetchNextPage
                            })
                        }
                    </div>
                </Sidebar>
            </div>
        );
    }
});


module.exports = App;



/** WEBPACK FOOTER **
 ** ./js/app.js
 **/