// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        add_mode: false,
        is_hidden: true,        // hide add button on click
        add_post_content: "",
        add_name: "",
        cur_email: "",
        rows: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.add_post = function () {
        axios.post(add_post_url,
            {
                post_content: app.vue.add_post_content,
                name: app.vue.add_name,
            }).then(function (response) {
            app.vue.rows.push({
                id: response.data.id,
                post_content: app.vue.add_post_content,
                name: app.vue.add_name,
                like: 0,
                dislike: 0,
            });
            app.enumerate(app.vue.rows);
            app.thumbs_init(app.vue.rows);
            app.reset_form();
            app.set_add_status(false);
            app.set_is_hidden(true);
            app.init();
        });
    };

    app.reset_form = function () {
        app.vue.add_post_content = "";
    };  

    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };

    app.set_is_hidden = function (new_status) {
        app.vue.is_hidden = new_status;
    };

    app.delete_post = function(row_idx) {
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_post_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.rows.length; i++) {
                if (app.vue.rows[i].id === id) {
                    app.vue.rows.splice(i, 1);
                    app.enumerate(app.vue.rows);
                    break;
                }
            }
            });
    };
    
    app.thumbs_init = posts => {
        posts.map((post) =>{
            post.like = 0;
            post.dislike = 0;
            post.up_thumb_displayed = 0;
            post.down_thumb_displayed = 0;
            post.likers = "";
            post.dislikers = "";
        })
    }
    app.set_thumbs = function (r_idx, picked_thumb) {
        let post = app.vue.rows[r_idx];
        // put if statements here
        // if liked is clicked
        if(picked_thumb == 'up_thumb') {
            // if up thumb is empty
            if(post.like == 0){
                post.up_thumb_displayed = post.like = 1;
                post.down_thumb_displayed = post.dislike = 0;
            }
            // if up thumb is already clicked
            else if(post.like == 1){
                post.up_thumb_displayed = post.like = 0;
                post.down_thumb_displayed = post.dislike = 0;
            }
        }
        // else disliked is clicked
        else if(picked_thumb == 'down_thumb'){
            // if down thumb is empty
            if(post.dislike == 0){
                post.up_thumb_displayed = post.like = 0;
                post.down_thumb_displayed = post.dislike = 1;
            }
            // if down thumb is already clicked
            else if(post.dislike == 1){
                post.up_thumb_displayed = post.like = 0;
                post.down_thumb_displayed = post.dislike = 0;
            }
        }
        axios.post(set_thumbs_url, {posts_id: post.id, like: post.like, dislike: post.dislike});
        app.init();
    };

    app.thumb_over = function (post_idx, picked_thumb) {
        let post = app.vue.rows[post_idx];
        // if liked is clicked
        if(picked_thumb == 'up_thumb') {
            // if up thumb is empty
            if(post.like == 0){
                post.up_thumb_displayed = 1;
                post.down_thumb_displayed = 0;
            }
            // if up thumb is already clicked
            else if(post.like == 1){
                post.up_thumb_displayed = 0;
                post.down_thumb_displayed = 0;
            }
        }
        // else disliked is clicked
        else if(picked_thumb == 'down_thumb'){
            // if down thumb is empty
            if(post.dislike == 0){
                post.up_thumb_displayed = 0;
                post.down_thumb_displayed = 1;
            }
            // if down thumb is already clicked
            else if(post.dislike == 1){
                post.up_thumb_displayed = 0;
                post.down_thumb_displayed = 0;
            }
        }
    };

    app.thumb_out = function (post_idx) {
        let post = app.vue.rows[post_idx];
        post.up_thumb_displayed = post.like;
        post.down_thumb_displayed = post.dislike;
    };
    

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        add_post: app.add_post,
        set_add_status: app.set_add_status,
        delete_post: app.delete_post,
        set_is_hidden: app.set_is_hidden,
        set_thumbs: app.set_thumbs,
        thumb_over: app.thumb_over,
        thumb_out: app.thumb_out,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    // Generally, this will be a network call to the server to
    // load the data.
    // For the moment, we 'load' the data from a string.
    app.init = () => {
        // first get the posts
        axios.get(load_posts_url)
        .then(function (response) {
            // app.vue.rows = app.enumerate(response.data.rows);
            app.vue.cur_email = response.data.email;
            let posts = response.data.rows;
            app.thumbs_init(posts);
            app.enumerate(posts);
            
            app.vue.rows = posts;
        })
        .then(() => {
            //get the rating of each post
            for(let row of app.vue.rows){
                axios.get(get_thumbs_url, {params: {posts_id: row.id}})
                .then ((response) => {
                    row.like = response.data.like;
                    row.dislike = response.data.dislike;
                    row.up_thumb_displayed = response.data.like;
                    row.down_thumb_displayed = response.data.dislike;
                    row.likers = response.data.likers;
                    row.dislikers = response.data.dislikers;
                });
            }
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
