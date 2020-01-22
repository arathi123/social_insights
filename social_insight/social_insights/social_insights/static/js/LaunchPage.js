import React from 'react';

var pStyle = { backgroundColor: '#CCCCCC' };
var LaunchPage = React.createClass({

    componentDidMount() {
        console.log("hey");
    },

    render() {
        return (
            <div>

        <div className='small-12 column row post-row mainCanvas'  >
            <div className='row'>
            <div className='small-12 large-12 column infoBox'> 
            	<h5 className='small-12 large-12 column'  >
		         <p className='small-12 large-12 column' style={pStyle}>
		          { this.props.noFeed ?  'Contents will be updated when we have successfully collected the data from facebook' : '' }
		         </p>
		         <br/> <br/>
		        </h5>
		        <br/>
		     </div>
		      <div className='small-12 large-4 column infoBox'> 
		      	  <h6 className='subheader'> Feed for </h6>
		      	  <h4> Complaints </h4>	
		      	  <i className='fi-alert size-100'/>	
		      	  <p>
				      Sosilee provides a feed of complaints in any business's Facebook page.
				 </p>
			  </div>
		      <div className='small-12  large-4 column infoBox'> 
		      	  <h6 className='subheader'> Track complaints in your </h6>
		      	  <h4> Facebook pages </h4>	
		      	  <i className='fi-social-facebook size-100'/>	
		      	  <p>
				      Search the facebook page of your favorite business and start following it. 
				  </p>
			  </div>
		      <div className='small-12 large-4 column infoBox'> 
		      	  <h6 className='subheader'> Intelligent techniques for </h6>
		      	  <h4> Complaint detection </h4>	
		      	  <i className='fi-lightbulb size-100'/>	
		      	  <p>
				      Sosilee uses text mining and sentiment analysis techniques to filter the complaints from a Facebook page 
				  </p>
		      </div>
      		</div>
		</div>
      </div>
        );
    }
});

module.exports = LaunchPage;
