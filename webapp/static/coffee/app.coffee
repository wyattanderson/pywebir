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
    state.url = options.stateUrl
    state.set 'id', _.uniqueId()

    stateView = new StateView
        model: state
    IRApp.display.show stateView

    state.on 'change', ->
        stateView.render()

    state.on 'request', ->
        IRApp.trigger.apply IRApp, ['state-request', arguments...]

    state.on 'sync', ->
        IRApp.trigger.apply IRApp, ['state-sync', arguments...]

    collectionView.on 'itemview:click', (itemView, id, cb) ->
        state.save
            _button: id
        ,
            patch: true

    handleVisibilityChange = ->
        if document.hidden
            return

        do state.fetch

    document.addEventListener('visibilitychange', handleVisibilityChange)

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

    onShow: ->
        @listenTo IRApp, 'state-request', =>
            @ui.button.attr 'disabled', 'disabled'
        @listenTo IRApp, 'state-sync', =>
            @ui.button.removeAttr 'disabled'

    handleAction: (event) ->
        @trigger 'click', @model.get('id')

class ButtonCollectionView extends Backbone.Marionette.CollectionView
    tagName: 'ul'
    className: 'button-collection-view'
    itemView: ButtonView

class StateView extends Backbone.Marionette.ItemView
    template: '#state-view'
    className: 'state-view'

    ui:
        spinner: '.spinner'

    onRender: ->
        if @model.get 'power'
            @$el.addClass('power-on')
                .removeClass('power-off')
        else
            @$el.addClass('power-off')
                .removeClass('power-on')

        @listenTo IRApp,
            'state-request': =>
                @$el.addClass 'state-syncing'
            'state-sync': =>
                @$el.removeClass 'state-syncing'
