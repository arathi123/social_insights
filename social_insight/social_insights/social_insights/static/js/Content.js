import React from 'react';
import PostContent from './PostContent.js';
import LaunchPage from './LaunchPage.js';

var Content = React.createClass({
    getdata() {
        let options = {
            page: 1,
            sm_account_id: this.props.params.id,
            access_token: userInfo.access_token
        };
        this.props.getFeed(options);
    },


    componentDidMount() {
        this.getdata();
    },


    componentDidUpdate(prevProps) {
        let oldId = prevProps.params.id
        let newId = this.props.params.id
        if (newId !== oldId) {
            this.getdata();
        }
    },


    render() {
        if (this.props.feed.length != 0) {
            return (
                <div id='mainContent' className='large-12 column' >
                  <PostContent messages={this.props.feed} fetchNextPage={this.props.fetchNextPage} />
                </div>
            );
        } else {
            return (
                <div id='mainContent' className='large-12 column' >
                  <LaunchPage noFeed={'true'} />
                </div>
            );
        }
    }


});

module.exports = Content;
