import React from 'react';
import ReactList from 'react-list';

var PostRow = React.createClass({
    render() {
        if (this.props.comment.message) {
            var imageUrl = "http://graph.facebook.com/" + this.props.comment.from.id + "/picture?type=square";
            return (
                <div className='post-row'  >
                    <div className='row'>
                        <img className='small-2 large-1 column' src={imageUrl}/>
                        <h6 className='small-6 large-8 column end'> 
                            <a className='profileLink' href={'https://www.facebook.com/'+this.props.comment.from.id} target='_blank'>
                            {this.props.comment.from.name }
                            </a>  
                            {' >'} {this.props.comment.account_name}
                            <p className='timestampContent'> {jQuery.timeago(this.props.comment.created_time)} </p>
                        </h6>
                        <a className='see-fb small-1 column' href={'https://www.facebook.com/'+this.props.comment.id} target='_blank'>
                            <i data-tooltip className='see-fb small-1 column fi-eye size-24 has-tip' title='See in facebook'/>
                        </a>
                    </div>
                    <p> {this.props.comment.message} </p>
                </div>
            );
        } else {
            return null;
        }
    }
});

var PostContent = React.createClass({
    renderItem(index, key) {
        if (index == this.props.messages.length - 5) {
            this.props.fetchNextPage();
        }
        return (
            <PostRow key={key} comment={this.props.messages[index]}/>
        );
    },
    render() {
        return (
            <ReactList
            itemRenderer={this.renderItem}
            length={this.props.messages.length}
            type='variable'
            pageSize = {10}          
          />
        );
    }
});

module.exports = PostContent;
