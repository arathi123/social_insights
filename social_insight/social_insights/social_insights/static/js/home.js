import React from 'react';
import PostContent from './PostContent.js';

var Home = React.createClass({
    getdata() {
        let options = { page: 1, access_token: userInfo.access_token };
        this.props.getFeed(options);
    },

    highlightSelection() {
        if ($('#pageList').find('.selectedItem').size() != 0) {
            var prevElement = $('#pageList').find('.selectedItem')[0]
            prevElement.className = "paneItem";
        }
    },

    componentDidMount() {
        this.highlightSelection();
        this.getdata();
    },

    getContent() {
        if (this.props.smAccounts.length == 0) {
            return (
                <div>
                    <div className="row">
                        <div className='small-12 column'>
                            <h6 className='subheader'> Get a feed of complaints </h6>
                            <p> Search any brand's facebook page and start following it. 
                            <span> Tip: </span> Try following <em> Amazon India </em> and <em>FlipKart</em> </p>
                        </div>
                    </div>
                    <img src="/static/ demo.gif" width="100%"/>
                </div>
            );
        } else {
            return (
                <PostContent messages={this.props.feed} fetchNextPage={this.props.fetchNextPage} />
            );
        }

    },

    render() {
        var content = this.getContent();
        return (
            <div id='mainContent' className='large-12 column'>
            { content }
            </div>
        )
    }


});

module.exports = Home;
