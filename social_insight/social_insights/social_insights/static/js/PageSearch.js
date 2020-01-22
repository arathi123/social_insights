import React from 'react';
import ReactDOM from 'react-dom';
import Autosuggest from 'react-autosuggest';
import { browserHistory, Router, Route, Link, withRouter } from 'react-router'
import React from 'react';
import ReactDOM from 'react-dom';
import Autosuggest from 'react-autosuggest';
import { browserHistory, Router, Route, Link, withRouter } from 'react-router'

// https://developer.mozilla.org/en/docs/Web/JavaScript/Guide/Regular_Expressions#Using_Special_Characters
function escapeRegexCharacters(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function getSuggestions(value) {
    const escapedValue = escapeRegexCharacters(value.trim());

    if (escapedValue === '') {
        return [];
    }

    const regex = new RegExp('^' + escapedValue, 'i');

    return languages.filter(language => regex.test(language.name));
}

function getSuggestionValue(suggestion) {
    return suggestion.name;
}

function renderSuggestion(suggestion) {
    return (
        <span>{suggestion.name}</span>
    );
}

class PageSearch extends React.Component {
    constructor() {
        super();

        this.state = {
            value: '',
            suggestions: [],
            isLoading: false
        };

        this.onChange = this.onChange.bind(this);
        this.onSuggestionsUpdateRequested = this.onSuggestionsUpdateRequested.bind(this);
        this.setSuggestions = this.setSuggestions.bind(this);
        this.onSuggestionSelected = this.onSuggestionSelected.bind(this);
        this.shouldRenderSuggestions = this.shouldRenderSuggestions.bind(this);
    }

    setSuggestions(value, suggestions) {
        var min_100_fans = suggestions.filter(function(page) {
            return page.fan_count > 100;
        });
        min_100_fans.sort(function(suggestion, otherSuggestion) {
            return -(suggestion.fan_count - otherSuggestion.fan_count);
        });
        min_100_fans = min_100_fans.slice(0, 10);
        if (value === this.state.value) {
            this.setState({
                isLoading: false,
                suggestions: min_100_fans
            });
        } else { // Ignore suggestions if input value changed
            this.setState({
                isLoading: false
            });
        }
    }

    loadSuggestions(value) {
        this.setState({
            isLoading: true
        });

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
                const suggestions = data.data;
                this.setSuggestions(value, suggestions);
            }.bind(this)
        });
    }

    onChange(event, { newValue, method }) {
        this.setState({
            value: newValue
        });
    }

    shouldRenderSuggestions(value) {
        return value.trim().length > 2;
    }

    onSuggestionSelected(event, { suggestion, suggestionValue, sectionIndex, method }) {
        console.log('The selected value is ' + suggestionValue);
        console.log(suggestion);
        this.props.selectionHandler(suggestion);
        this.props.toggleOpen();
        this.props.router.push({ pathname: "/follow/" + suggestion.id + "/" + suggestion.name, state: suggestion });
        this.setState({ value: '' });
        // ReactDOM.findDOMNode(this.refs.autosuggest.input).value = '';
        // this.refs.autosuggest.props.inputProps.value = '';
        // this.refs.autosuggest.input.value = '';
        // this.refs.autosuggest.input.focus();


    }

    onSuggestionsUpdateRequested({ value }) {
        this.loadSuggestions(value);
    }

    render() {
        const { value, suggestions } = this.state;
        const inputProps = {
            placeholder: "Add a new FB page",
            id: "page_search",
            value,
            onChange: this.onChange
        };

        return (
            <Autosuggest ref="autosuggest" suggestions={suggestions}
                   onSuggestionsUpdateRequested={this.onSuggestionsUpdateRequested}
                   getSuggestionValue={getSuggestionValue}
                   renderSuggestion={renderSuggestion}
                   inputProps={inputProps}
                   onSuggestionSelected={this.onSuggestionSelected}
                   shouldRenderSuggestions={this.shouldRenderSuggestions}
                   id={'page-search'} />
        );
    }
}

// module.exports = PageSearch;

export default withRouter(PageSearch)

// https://developer.mozilla.org/en/docs/Web/JavaScript/Guide/Regular_Expressions#Using_Special_Characters
function escapeRegexCharacters(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function getSuggestions(value) {
    const escapedValue = escapeRegexCharacters(value.trim());

    if (escapedValue === '') {
        return [];
    }

    const regex = new RegExp('^' + escapedValue, 'i');

    return languages.filter(language => regex.test(language.name));
}

function getSuggestionValue(suggestion) {
    return suggestion.name;
}

function renderSuggestion(suggestion) {
    return (
        <span>{suggestion.name}</span>
    );
}

class PageSearch extends React.Component {
    constructor() {
        super();

        this.state = {
            value: '',
            suggestions: [],
            isLoading: false
        };

        this.onChange = this.onChange.bind(this);
        this.onSuggestionsUpdateRequested = this.onSuggestionsUpdateRequested.bind(this);
        this.setSuggestions = this.setSuggestions.bind(this);
        this.onSuggestionSelected = this.onSuggestionSelected.bind(this);
        this.shouldRenderSuggestions = this.shouldRenderSuggestions.bind(this);
    }

    setSuggestions(value, suggestions) {
        var min_100_fans = suggestions.filter(function(page) {
            return page.fan_count > 100;
        });
        min_100_fans.sort(function(suggestion, otherSuggestion) {
            return -(suggestion.fan_count - otherSuggestion.fan_count);
        });
        min_100_fans = min_100_fans.slice(0, 10);
        if (value === this.state.value) {
            this.setState({
                isLoading: false,
                suggestions: min_100_fans
            });
        } else { // Ignore suggestions if input value changed
            this.setState({
                isLoading: false
            });
        }
    }

    loadSuggestions(value) {
        this.setState({
            isLoading: true
        });

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
                const suggestions = data.data;
                this.setSuggestions(value, suggestions);
            }.bind(this)
        });
    }

    onChange(event, { newValue, method }) {
        this.setState({
            value: newValue
        });
    }

    shouldRenderSuggestions(value) {
        return value.trim().length > 2;
    }

    onSuggestionSelected(event, { suggestion, suggestionValue, sectionIndex, method }) {
        console.log('The selected value is ' + suggestionValue);
        console.log(suggestion);
        this.props.selectionHandler(suggestion);
        this.props.toggleOpen();
        this.props.router.push({ pathname: "/follow/" + suggestion.id + "/" + suggestion.name, state: suggestion });
        this.setState({ value: '' });
        // ReactDOM.findDOMNode(this.refs.autosuggest.input).value = '';
        // this.refs.autosuggest.props.inputProps.value = '';
        // this.refs.autosuggest.input.value = '';
        // this.refs.autosuggest.input.focus();


    }

    onSuggestionsUpdateRequested({ value }) {
        this.loadSuggestions(value);
    }

    render() {
        const { value, suggestions } = this.state;
        const inputProps = {
            placeholder: "Add a new FB page",
            id: "page_search",
            value,
            onChange: this.onChange
        };

        return (
            <Autosuggest ref="autosuggest" suggestions={suggestions}
                   onSuggestionsUpdateRequested={this.onSuggestionsUpdateRequested}
                   getSuggestionValue={getSuggestionValue}
                   renderSuggestion={renderSuggestion}
                   inputProps={inputProps}
                   onSuggestionSelected={this.onSuggestionSelected}
                   shouldRenderSuggestions={this.shouldRenderSuggestions}
                   id={'page-search'} />
        );
    }
}

// module.exports = PageSearch;

export default withRouter(PageSearch)
