/*
 * Copyright: Copyright (c) 2020., Adam Jakab
 *
 * Author: Adam Jakab <adam at jakab dot pro>
 * License: MIT
 */

-- DATABASE STRUCTURE

-- drop table card_attributes;
-- drop table cards;
-- drop table users;

create table users
(
    username varchar(64)  not null
        constraint users_pk
            primary key,
    secret   varchar(255) not null
);

create table cards
(
    id         char(36)    not null
        constraint card_pk
            primary key,
    parent_id  char(36),
    owner      varchar(64) not null
        constraint FK_users
            references users (username) on update restrict on delete restrict,
    collection varchar(32) not null,
    name       varchar(64) not null,
    identifier varchar(255),
    created    char(20) default (datetime('now', 'localtime')) not null,
    modified   char(20) default (datetime('now', 'localtime')) not null
);

create index cards_idx_owner on cards (owner ASC);
create index cards_idx_collection on cards (collection ASC);
create index cards_idx_name on cards (name ASC);

create table card_attributes
(
    card_id  char(36)    not null
        constraint FK_cards
            references cards on update cascade on delete cascade,
    key      varchar(32) not null,
    value    text,
    created  char(20) default (datetime('now', 'localtime')) not null,
    modified char(20) default (datetime('now', 'localtime')) not null,
    constraint card_attributes_pk
        primary key (card_id, key)
);
