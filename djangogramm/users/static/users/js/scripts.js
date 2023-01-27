function csrf() {

}

function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

//Get Likes Statistic
function likesGetStatistic(el, post_id) {
    $.getJSON("/api/like-info/" + post_id + '/', (data) => {
        console.log(data)
        $(el).find('.like-btn-wrap .likes-qty').empty();
        $(el).find('.like-btn-wrap .likes-qty').text(data[0]['likes_count'])
    })
}

//Get Users Statistic
function usersGetStatistic(el, user_id, foreign_user_id) {
    $.getJSON("../../api/follow-info/" + user_id + '/' + foreign_user_id + '/', (data) => {
        console.log(data)
        $(el).find('.follow-btn-wrap .follows-qty').empty();
        $(el).find('.follow-btn-wrap .follows-qty').text(data[0]['follows_count'])
        $(el).find('.follow-btn-wrap .followers-qty').empty();
        $(el).find('.follow-btn-wrap .followers-qty').text(data[1]['followers_count']);
        $('.followers-span .fl-qty').text(data[1]['followers_count']);
    })
}

function likesGet_likes_id(el, post_id) {
    $.getJSON("/api/like-info/" + post_id + "/", (data) => {
        let likes_from_users_id = data[1]['likes_from_users'][0]['id'];
        $(el).find('input[name="likes_id"]').val('');
        $(el).find('input[name="likes_id"]').val(likes_from_users_id);
    })
}

// Ajax add\remove follower
function addRemoveFollower() {
    const csrftoken = getCookie('csrftoken');

    $('form.add-remove-follower').each((index, el) => {
        $(el).on('submit', (e) => {
            e.preventDefault();
            // console.log(e.currentTarget);

            const user_id = $(el).find('input[name="user_id"]').val();
            const foreign_user_id = $(el).find('input[name="foreign_user_id"]').val();

            if ($(e.currentTarget).hasClass('add-follower')) {
                $.ajax({
                    url: "/ajax/follow-add/",
                    type: "POST",
                    dataType: "json",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": csrftoken,
                    },
                    data: {
                        foreign_user_id: foreign_user_id,
                        user_id: user_id,
                    },

                    success: (data) => {
                        console.log(data);

                        if (data['added']) {
                            $(el).removeClass('add-follower').addClass('remove-follower');
                            $(el).attr('action', '/ajax/follow-remove/');

                            $(el).find('.follow-btn-wrap').empty();
                            $(el).find('.follow-btn-wrap').html('<button type="submit" class="btn btn-outline-dark" data-mdb-ripple-color="dark"\n' +
                                'style="z-index: 1;">\n' +
                                'Отписаться\n' +
                                '</button>')
                        }
                        usersGetStatistic(el, user_id, foreign_user_id);
                    }
                });
            }
            if ($(e.currentTarget).hasClass('remove-follower')) {
                $.ajax({
                    url: "/ajax/follow-remove/",
                    type: "POST",
                    dataType: "json",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": csrftoken,
                    },

                    data: {
                        foreign_user_id: foreign_user_id,
                        user_id: user_id,
                    },

                    success: (data) => {
                        console.log(data);

                        if (data['removed']) {
                            $(el).removeClass('remove-follower').addClass('add-follower');
                            $(el).attr('action', '/ajax/follow-add/');
                            $(el).find('.follow-btn-wrap').empty();
                            $(el).find('.follow-btn-wrap').html('<button type="submit" class="btn btn-outline-dark" data-mdb-ripple-color="dark"\n' +
                                'style="z-index: 1;">\n' +
                                'Подписаться\n' +
                                '</button>'
                            );
                        }
                        usersGetStatistic(el, user_id, foreign_user_id);
                    }
                });
            }
        })
    })
}

//Ajax add/remove like
function addRemoveLike() {
    const csrftoken = getCookie('csrftoken');
    $('form.add-remove-like').each((index, el) => {
        $(el).on('submit', (e) => {
            e.preventDefault();

            //console.log(e);
            //console.log(e.currentTarget);

            const post_id = $(el).find('input[name="post_id"]').val();
            const user_id = $(el).find('input[name="user_id"]').val();
            const likes_id = $(el).find('input[name="likes_id"]').val();

            if ($(e.currentTarget).hasClass('add-like')) {
                $.ajax({
                    url: "/ajax/add/",
                    type: "POST",
                    dataType: "json",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": csrftoken,
                    },
                    data: {
                        post_id: post_id,
                        user_id: user_id,
                    },
                    success: (data) => {
                        console.log(data);

                        if (data['added']) {
                            $(el).removeClass('add-like').addClass('remove-like');
                            $(el).attr('action', '/ajax/remove');

                            $(el).find('.like-btn-wrap').empty();
                            $(el).find('.like-btn-wrap').html('<button type="submit" class="remove-like-btn btn btn-danger">' +
                                '<i class="fa fa-heart"></i>' +
                                '<span class="likes-qty" style="padding-left: 5px"></span>' +
                                '</button>');
                        }

                        likesGetStatistic(el, post_id);
                        likesGet_likes_id(el, post_id);
                    }
                });
            }

            if ($(e.currentTarget).hasClass('remove-like')) {
                $.ajax({
                    url: "/ajax/remove/",
                    type: "POST",
                    dataType: "json",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": csrftoken,
                    },

                    data: {
                        post_id: post_id,
                        user_id: user_id,
                        likes_id: likes_id
                    },

                    success: (data) => {
                        console.log(data);

                        if (data['removed']) {
                            $(el).removeClass('remove-like').addClass('add-like');
                            $(el).attr('action', '/ajax/add/');

                            $(el).find(".like-btn-wrap").empty();
                            $(el).find(".like-btn-wrap").html('<button type="submit" class="add-like-btn btn btn-outline-danger">' +
                                '<i class="fa fa-heart-o"></i>' +
                                '<span class="likes-qty" style="padding-left: 5px"></span>' +
                                '</button>');
                        }
                        likesGetStatistic(el, post_id);
                    }
                })
            }
        })
    })
}

$(document).ready(() => {
    csrf();

    addRemoveLike();
    addRemoveFollower();
});