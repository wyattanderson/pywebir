IRApp = new Backbone.Marionette.Application

IRApp.addRegions
    content: '#content'

IRApp.addInitializer (options) ->
    new FastClick document.body
    do Backbone.history.start
    $(window).load ->
        _.defer ->
            window.scrollTo 0, 1

IRApp.on 'start', (options) ->
    binCollection = new BinCollection options.bins
    collectionView = new BinCollectionView
        collection: binCollection
    IRApp.content.show collectionView

class BinCollection extends Backbone.Collection

class ButtonView extends Backbone.Marionette.ItemView
    tagName: 'li'
    template: '#button-view'
    events:
        'click .action': 'handleAction'
    ui:
        button: 'button'

    handleAction: (event) ->
        @ui.button.attr 'disabled', 'disabled'
        $.ajax
            url: "/do-bin/#{@model.get 'id'}/"
            success: =>
                @ui.button.removeAttr 'disabled'

class BinCollectionView extends Backbone.Marionette.CollectionView
    tagName: 'ul'
    className: 'bin-collection-view'
    itemView: ButtonView
