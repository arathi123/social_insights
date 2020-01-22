
CREATE TABLE categories (
    category_id integer NOT NULL,
    name character varying(45),
    category_group_id integer NOT NULL
);



CREATE TABLE category_groups (
    category_group_id integer NOT NULL,
    name character varying(45)
);


CREATE TABLE posts (
    post_id bigint NOT NULL,
    parent_post_id bigint,
    post_text text,
    created_timestamp timestamp without time zone,
    sm_account_id integer NOT NULL
);

CREATE TABLE sm_accounts (
    sm_account_id bigint NOT NULL,
    sm_domain character varying(250),
    sm_url character varying(250)
);

CREATE TABLE user_post_categories (
    user_id bigint NOT NULL,
    post_id bigint NOT NULL,
    category_id integer NOT NULL,
    created_timestamp timestamp without time zone
);


CREATE TABLE users (
    user_id bigint NOT NULL,
    user_email character varying(250),
    fb_user_name character varying(250),
    access_token character varying(300)
);




CREATE TABLE users_sm_accounts (
    user_id bigint NOT NULL,
    sm_account_id bigint NOT NULL,
    user_sm_account_id integer NOT NULL
);



ALTER TABLE ONLY categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);



ALTER TABLE ONLY category_groups
    ADD CONSTRAINT category_groups_pkey PRIMARY KEY (category_group_id);



ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (post_id, sm_account_id);



ALTER TABLE ONLY sm_accounts
    ADD CONSTRAINT sm_accounts_pkey PRIMARY KEY (sm_account_id);




ALTER TABLE ONLY user_post_categories
    ADD CONSTRAINT user_post_categories_pkey PRIMARY KEY (user_id, post_id, category_id);




ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);




ALTER TABLE ONLY users_sm_accounts
    ADD CONSTRAINT users_sm_accounts_pkey PRIMARY KEY (user_sm_account_id);




ALTER TABLE ONLY categories
    ADD CONSTRAINT fk_categories_category_sets1 FOREIGN KEY (category_group_id) REFERENCES category_groups(category_group_id);




ALTER TABLE ONLY posts
    ADD CONSTRAINT fk_posts_sm_accounts1 FOREIGN KEY (sm_account_id) REFERENCES sm_accounts(sm_account_id);




ALTER TABLE ONLY user_post_categories
    ADD CONSTRAINT fk_user_post_categories_1 FOREIGN KEY (user_id) REFERENCES users(user_id);




ALTER TABLE ONLY user_post_categories
    ADD CONSTRAINT fk_user_post_categories_3 FOREIGN KEY (category_id) REFERENCES categories(category_id);



ALTER TABLE ONLY users_sm_accounts
    ADD CONSTRAINT fk_users_has_sm_accounts_sm_accounts1 FOREIGN KEY (sm_account_id) REFERENCES sm_accounts(sm_account_id);




ALTER TABLE ONLY users_sm_accounts
    ADD CONSTRAINT fk_users_has_sm_accounts_users FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE TABLE authenticated_users(
    auth_tkt VARCHAR(200) PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    last_active_time TIMESTAMP);



