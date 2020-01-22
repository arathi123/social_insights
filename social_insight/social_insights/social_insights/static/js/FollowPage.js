import React from 'react';
import Update from 'react-addons-update';
import { History } from "react-router"

var FollowPage = React.createClass({
    getFollowStatus(pageId) {
        var following = this.props.smAccounts.some(function(elem) {
            return elem.id == pageId
        }.bind(this));
        return following;
    },
    getInitialState() {
        return {
            'following': this.getFollowStatus(this.props.params.id),
            'fan_count': '',
            'about': ''
        };
    },

    getSuggestionObject(value) {

        $.ajax({
            dataType: "json",
            url: 'https://graph.facebook.com/v2.6/search',
            data: {
                q: value,
                type: 'page',
                fields: 'id,name,about,fan_count',
                access_token: userInfo.access_token
            },
            success: function(data) {
                const suggestions = data.data[0];
                this.setState({ 'fan_count': suggestions.fan_count, 'about': suggestions.about });

            }.bind(this)
        });

    },

    handleSubmit(event) {
        event.preventDefault();
        if (!this.state.following) {
            $('#follow-button').hide();
            $('#fb-delay-info').show();
        }
        $.ajax({
            type: "POST",
            url: '/sm_accounts',
            data: {
                sm_account_id: this.props.params.id,
                sm_domain: this.props.params.name,
                action: this.state.following ? 'unfollow' : 'follow'
            },
            success: function(status) {
                var smAccount = { 'id': this.props.params.id, 'name': this.props.params.name };
                if (this.state.following) {
                    this.props.handleFollowEvent(smAccount, 'unfollow');
                } else {
                    this.props.handleFollowEvent(smAccount, 'follow');
                }
                this.setState({ 'following': !this.state.following });
                $('#follow-button').show()
                $('#fb-delay-info').hide()
            }.bind(this)
        });
    },

    componentWillReceiveProps(nextProps) {
        if (this.props.location.state == null) {
            this.getSuggestionObject(nextProps.params.name);
        }
        var following = this.getFollowStatus(nextProps.params.id);
        this.setState({ 'following': following });
    },

    infoOfFanAndAbout() {
        if (this.props.location.state != null) {
            return (
                <div> <h6 className='subheader'> {this.props.location.state.fan_count + ' Fans'} </h6>
                <p> { this.props.location.state.about } </p>
                </div>
            );
        } else {
            return (
                <div> <h6 className='subheader'> {this.state.fan_count + ' Fans'} </h6>
                <p> { this.state.about } </p>
                </div>
            );
        }
    },

    render() {
        var imageUrl = "http://graph.facebook.com/" + this.props.params.id + "/picture?type=large";
        return (
            <form onSubmit={this.handleSubmit}>
                <div className='small-12 column row post-row mainCanvas' >
                    <div className='small-3 column '>
                        <img src={imageUrl} style={{'height':'200px'}} />
                    </div>
                    <div className='small-9 column' >
                      <h4> 
                        <a href={'http://facebook.com/'+this.props.params.id} target='_blank'> 
                            {this.props.params.name} 
                        </a>
                      </h4>
                        {this.infoOfFanAndAbout()}
                      <input id="follow-button" 
                        type="submit" value={this.state.following ? 'Following':'Follow'} 
                        className={this.state.following ? 'button success':'button'}
                        />
                       <div id="fb-delay-info" className="callout" style={{'display': 'none'}}>
                            <div className="small-12 column row">
                                <img src="/static/images/hourglass.gif" className="small-2 column"/>
                                <div className="small-10 column">
                                    <h5> Loading data from facebook </h5>
                                    <p>  This might take few seconds. Thank you for your patience.
                                    </p>
                                </div>
                            </div>
                       </div> 
                    </div>
                </div>
            </form>
        );
    }
});

module.exports = FollowPage;
