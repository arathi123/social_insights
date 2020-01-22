import React from 'react'
import { render } from 'react-dom'
import { browserHistory, Router, Route, Link, withRouter } from 'react-router'

import 'script!jquery';
import 'script!foundation-sites/dist/foundation.min.js';
import 'script!timeago';
import Update from 'react-addons-update';

var Taco = React.createClass({

  remove() {
    this.props.onRemoveTaco(this.props.params.name)
  },

  fakeAjax(name) {
    this.props.tacos.map(function (taco, i) {
      if(taco.name==name){
        console.log(taco.id);

      }
    });
  },

   // componentDidMount() {
   //   setTimeout(() => {
   //     this.fakeAjax(this.props.params.name)
   //   }, 1000);
   // },  

  render() {
    this.fakeAjax(this.props.params.name);
    return (
      <div className="Taco">
        <h1>{this.props.params.name}</h1>
        <button onClick={this.remove}>remove</button>
      </div>
    );
  }
});


module.exports = Taco;