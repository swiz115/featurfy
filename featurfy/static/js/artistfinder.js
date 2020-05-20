let selectArtistId = ''
let relatedArtistDic = {}
let relatedArtistArray = []


function getSuitableImage(images) {
    let minSize = 64;
    if (images.length === 0) {
        return '/static/images/logo.png';
    }
    images.forEach(function (image) {
        if (image && image.width > minSize && image.width > 64) {
            return image.url;
        }
    });
    return images[images.length - 1].url;
}

function createAutoCompleteDiv(artist) {
    if (!artist) {
        return;
    }
    let val = '<div class="autocomplete-item">' +
        '<div>' +
        '<img src="' + getSuitableImage(artist.images) + '" class="circular artist-icon" />' +
        '<div id=artist-' + artist.id + ' class="artist-label">' + artist.name + '</div>' +
        '</div>' +
        '</div>';
    return val;
}

function createRelatedArtist(artistId){

    let followHtml = "<i class='fa fa-close'></i>"
    if(relatedArtistDic[artistId]['follow']){
        followHtml = "<i class='fa fa-check'></i>"
    }
    let val =   
            '<div style="margin-bottom: 10px; padding-right: 15px;" class="row row-margin">' + 
            '<a href="' +relatedArtistDic[artistId]['uri'] + '"><img src="' + getSuitableImage(relatedArtistDic[artistId]['images']) + '" class="circular artist-icon" /></a>' +
                '<div class="col align-self-center">' +
                    '<div class="row">' + 
                        '<div class="col-5 text-left">' +
                            relatedArtistDic[artistId]['name'] +
                        '</div>' +
                        '<div class="col text-left">' +
                            relatedArtistDic[artistId]['popularity'] +
                        '</div>' +
                        '<div class="col text-left">' +
                            followHtml +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>'

    return val;
}

function createErrorMessage(msg){
    $('#load').css('display', 'none')
    let alertMsg = ''
    if(msg === 'request'){
        alertMsg = 'Oops! An error occured. Please try again.';
    }
    else if(msg === 'relatedartist'){
        alertMsg = 'Oops! This artist has no related artists. Please select another artist.';
    }
    else if(msg === 'search'){
        alertMsg = 'Oops! No matches could be found. Please enter a different artist.';
    }
    let alertHtml = 
                '<div id="alert-msg" style="margin-bottom: 0px; font-size: 90%" class="alert alert-danger alert-dismissible text-left">' + 
                    '<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' +
                     alertMsg +
                '</div>';

    $("#header").after(alertHtml);

    setTimeout(function () {
        $("#alert-msg").fadeTo(2000, 500).slideUp(500, function () {
            $("#alert-msg").remove();
        });   
    }, 5000);

}

async function artistSelectFetch(url) {
    const response = await fetch(url, {
        method: 'GET', 
        credentials: 'same-origin', 
        headers: {
        'Content-Type': 'application/json'
        },
    });
    return response; 
}

function artistSelect(){
    // Remove all children from related artist list
    let myNode = document.getElementById("related-artists-list");
    while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
    }
    $("#load").show();
    $("#artist-name-sort").remove();
    $("#following-sort").remove();
    $("#popularity-sort").remove();

    artistSelectFetch('/api/v1/relatedartist/' + selectArtistId)
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
        })
        .then((data) => {
            relatedArtistDic = data.related_artist_dic
            relatedArtistArray = data.related_artist_list
            if (Array.isArray(relatedArtistArray) && relatedArtistArray.length) {
                $('#load').css('display', 'none')
                for(let id of relatedArtistArray){
                    let artistHtml = createRelatedArtist(id);
                    $('#related-artists-list').append(artistHtml)
                }
            }
            else{
                createErrorMessage('relatedartist')
            }
        })
        .catch((error) => {
            if(error.status === 500 || error.status === 401 || error.status === 405){
                createErrorMessage('request');
                console.log('Error 500: error on spotify end');
                console.log('Error 401: session expire');
                console.log('Error 405: invalid method');
            }
        })
}

$( function() {
    $( "#artist-search" )
        .autocomplete({
            source: function (request, response) {
                let searchRequest = new Request('/api/v1/searchartist/' + request.term, {
                    method: 'GET', 
                    credentials: 'same-origin',
                    headers: new Headers({
                        'Content-Type': 'application/json'
                    }),
                });

                fetch(searchRequest)
                    .then((searchResponse) => {
                        if (!searchResponse.ok) throw Error(searchResponse.statusText);
                        return searchResponse.json();
                    })
                    .then((data) => {
                        if(data.artists && data.artists.length){
                            response(data.artists)
                        }
                        else{
                            createErrorMessage('search');
                            response([]);
                        }
                        
                    })
                    .catch((error) => {
                        if(error.status === 500 || error.status === 401 || error.status === 405){
                            createErrorMessage('request');
                            console.log('Error 500: error on spotify end');
                            console.log('Error 401: session expire');
                            console.log('Error 405: invalid method');
                        }
                    })
            },
            select: function (event, ui) {
                selectArtistId = ui.item.id
                $('#artist-search').val(ui.item.name);
                artistSelect();
                return false;
            }
        })
        .autocomplete('instance')._renderItem = function (ul, item) {
            if (!item) {
                return;
            }
            return $('<li></li>')
                .data('item.autocomplete', item)
                .append(createAutoCompleteDiv(item))
                .appendTo(ul);
        };
});

$('#search-artist').on('keyup keypress', function(e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) { 
        e.preventDefault();
        return false;
    }
});

$("#popularity-help").click(function() {
    if($('#popularity-description').css('display') === 'none'){
        $('#popularity-description').show();
    }
    else{
        $('#popularity-description').css('display', 'none')
    }
});

$("#artist-name-col").click(function() {
    if (relatedArtistArray.length === 0) {
        return;
    }
    if($("#artist-name-col").hasClass('asc')){
        sortRelatedArtist('name', 'desc');
        $("#artist-name-col").removeClass('asc');
        $("#artist-name-col").addClass('desc');

        $("#artist-name-sort").remove();
        $("#artist-name-col").after('<i id="artist-name-sort" style="font-size: 14px;" class="fa fa-sort-desc"></i>');
    }
    else{
        sortRelatedArtist('name', 'asc');
        $("#artist-name-col").removeClass('desc');
        $("#artist-name-col").addClass('asc');

        $("#artist-name-sort").remove();
        $("#artist-name-col").after('<i id="artist-name-sort" style="font-size: 14px;" class="fa fa-sort-asc"></i>');
    } 
});

$("#popularity-col").click(function() {
    if (relatedArtistArray.length === 0) {
        return;
    }
    if($("#popularity-col").hasClass('asc')){
        sortRelatedArtist('popularity', 'desc');
        $("#popularity-col").removeClass('asc');
        $("#popularity-col").addClass('desc');

        $("#popularity-sort").remove();
        $("#popularity-col").after('<i id="popularity-sort" style="font-size: 14px;" class="fa fa-sort-desc"></i>');
    }
    else{
        sortRelatedArtist('popularity', 'asc');
        $("#popularity-col").removeClass('desc');
        $("#popularity-col").addClass('asc');

        $("#popularity-sort").remove();
        $("#popularity-col").after('<i id="popularity-sort" style="font-size: 14px;" class="fa fa-sort-asc"></i>');
    }
    

});

$("#following-col").click(function() {
    if (relatedArtistArray.length === 0) {
        return;
    }
    if($("#following-col").hasClass('asc')){
        sortRelatedArtist('follow', 'desc');
        $("#following-col").removeClass('asc');
        $("#following-col").addClass('desc');

        $("#following-sort").remove();
        $("#following-col").after('<i id="following-sort" style="font-size: 14px;" class="fa fa-sort-desc"></i>');
    }
    else{
        sortRelatedArtist('follow', 'asc');
        $("#following-col").removeClass('desc');
        $("#following-col").addClass('asc');

        $("#following-sort").remove();
        $("#following-col").after('<i id="following-sort" style="font-size: 14px;" class="fa fa-sort-asc"></i>');
    }   
});

function sortRelatedArtist(column, sortType){
    if(sortType === 'desc'){
        if(column === 'name'){
            relatedArtistArray.sort(function(a, b){
                let nameA = relatedArtistDic[a][column].toUpperCase();
                let nameB = relatedArtistDic[b][column].toUpperCase();
                if(nameA > nameB){
                    return -1;
                }
                if(nameA < nameB){
                    return 1;
                }
                return 0;
            });
        }
        else{
            relatedArtistArray.sort(function(a, b){
                return relatedArtistDic[a][column] - relatedArtistDic[b][column]
            })
        }
    }
    else{
        if(column === 'name'){
            relatedArtistArray.sort(function(a, b){
                let nameA = relatedArtistDic[a][column].toUpperCase();
                let nameB = relatedArtistDic[b][column].toUpperCase();
                if(nameA < nameB){
                    return -1;
                }
                if(nameA > nameB){
                    return 1;
                }
                return 0;
            });
        }
        else{
            relatedArtistArray.sort(function(a, b){
                return relatedArtistDic[b][column] - relatedArtistDic[a][column]
            })
        }
    }
    let myNode = document.getElementById("related-artists-list");
    while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
    }
    for(let id of relatedArtistArray){
        let artistHtml = createRelatedArtist(id);
        $('#related-artists-list').append(artistHtml)
    }
}



