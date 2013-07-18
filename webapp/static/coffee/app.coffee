IRApp = new Backbone.Marionette.Application

IRApp.addRegions
    controls: '#controls'
    display: '#display'

IRApp.addInitializer (options) ->
    new FastClick document.body
    do Backbone.history.start
    $(window).load ->
        _.defer ->
            window.scrollTo 0, 1

IRApp.on 'start', (options) ->
    buttonCollection = new ButtonCollection options.buttons
    collectionView = new ButtonCollectionView
        collection: buttonCollection
    IRApp.controls.show collectionView

    state = new State options.state
    stateView = new StateView
        model: state
    IRApp.display.show stateView

    state.on 'change', ->
        stateView.render()

    collectionView.on 'itemview:click', (itemView, id, cb) ->
        $.ajax
            url: options.apiUrl.replace 'PLACEHOLDER', id
            success: (newState) ->
                state.set newState
                console.log state
                cb newState

class State extends Backbone.Model

class ButtonCollection extends Backbone.Collection
    comparator: (lhs, rhs) ->
        sort = 0
        if lhs.get('order') isnt rhs.get('order')
            sort = if lhs.get('order') < (rhs.get('order') ? Number.MAX_VALUE)
                -1
            else
                1
        else
            sort = 1

        sort

class ButtonView extends Backbone.Marionette.ItemView
    tagName: 'li'
    template: '#button-view'
    className: ->
        "button-#{@model.get 'id'}"
    events:
        'click .action': 'handleAction'
    ui:
        button: 'button'

    handleAction: (event) ->
        @trigger 'click', @model.get('id'), @onSuccess
        @ui.button.attr 'disabled', 'disabled'

    onSuccess: =>
        @ui.button.removeAttr 'disabled'

class ButtonCollectionView extends Backbone.Marionette.CollectionView
    tagName: 'ul'
    className: 'button-collection-view'
    itemView: ButtonView

class StateView extends Backbone.Marionette.ItemView
    template: '#state-view'
    className: 'state-view'

    onRender: ->
        if @model.get 'power'
            @$el.addClass('power-on')
                .removeClass('power-off')
        else
            @$el.addClass('power-off')
                .removeClass('power-on')
