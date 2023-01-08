import random
from datetime import datetime

from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_required, current_user

from mysql.db import save_sketch, get_user_id, get_username_by_id, connect_to_room, disconnect_from_room, get_all_rooms, get_connected_members, save_room, add_room_member, add_room_members, get_room, is_room_member, is_room_admin, get_room_members, get_sketches, update_room, remove_room_members, get_word_rows

rooms = Blueprint("rooms", __name__, static_folder="static",
                  template_folder="templates")


@rooms.route('/create-room/', methods=['GET', 'POST'])
@login_required
def create_room():
    message = ''
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        usernames = [username.strip() for username in request.form.get('members').split(',')]
        # check that usernames are registered users
        for username in usernames:
            valid_user = get_user_id(username)
            if not valid_user:
                flash("Must only include valid registered users")
                return redirect(url_for("rooms.create_room"))
        
        id = current_user.id
        user = current_user.username
        if len(room_name) and len(usernames):
            save_room(room_name, id)
            # take admin out of list if they added themselves
            if user in usernames:
                usernames.remove(user)
            add_room_members(room_name, usernames, id)
            connected_members = get_connected_members(room_name)
            return redirect(url_for('rooms.view_room', room_name=room_name, connected_members=connected_members))
        else:
            message = "Failed to create room"
    return render_template('create_room.html', message=message)


@rooms.route("/choose-room", methods=['GET', 'POST'])
@login_required
def choose_room():
    """Show choose_room view"""
    username = current_user.username
    if request.method == 'GET':
        # get all rooms
        rooms = get_all_rooms()
        # if no rooms, redirect to create_room
        if not rooms:
            return redirect(url_for("rooms.create_room"))
        # set expected data structure
        return render_template("join_room.html", username=username, rooms=rooms)

    room_name = request.form.get('roomSelect')
    id = current_user.id
    if not is_room_member(room_name, id):
        # room_member connected will be True on add_room_member
        add_room_member(room_name, id, id, False)
    connect_to_room(room_name, id)    
    return redirect(url_for('rooms.view_room', room_name=room_name))


@rooms.route('/view-room/<room_name>/')
@login_required
def view_room(room_name):
    room = get_room(room_name)
    if room:
        connected_members = get_connected_members(room_name)
        print(connected_members)
        return render_template('view_room.html', current_user=current_user, room_name=room_name, connected_members=connected_members)
    else:
        return "Room not found", 404


@rooms.route('/<room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = get_room(room_id)
    if room and is_room_admin(room_id, current_user.id):
        existing_room_members = []
        for member in get_room_members(room_id):
            user_id = member['user_id']
            username = get_username_by_id(user_id)
            existing_room_members.append(username)
        room_members_str = ", ".join(existing_room_members)
        
        message = ''
        if request.method == 'POST':
            room_name = request.form.get('room_name')
            room['name'] = room_name
            update_room(room_id, room_name)

            new_members = [username.strip() for username in request.form.get('members').split(',')]
            members_to_add = list(set(new_members) - set(existing_room_members))
            members_to_remove = list(set(existing_room_members) - set(new_members))
            if len(members_to_add):
                add_room_members(room_id, members_to_add, current_user.id)
            if len(members_to_remove):
                remove_room_members(room_id, members_to_remove)
            message = 'Room edited successfully'
            room_members_str = ",".join(new_members)
        return render_template('edit_room.html', room=room, room_members_str=room_members_str, message=message)
    else:
        return "Room not found", 404


@rooms.route('/<room_id>/sketches/')
@login_required
def get_older_sketches(room_id):
    room = get_room(room_id)
    if room and is_room_member(room_id, current_user.id):
        page = int(request.args.get('page', 0))
        sketches = get_sketches(room_id, page)
        return sketches
    else:
        return "Room not found", 404

@rooms.route('/<room_name>/<user_id>/disconnect/')
def disconnect(room_name, user_id):
    disconnect_from_room(room_name, user_id)
    return "room_member disconnected", 200

@rooms.route('/get_words/<difficulty>')
def get_words(difficulty):

    diff_ranges = [
        {'range': 'Easy', 'start': 1, 'end': 123},
        {'range': 'Med', 'start': 124, 'end': 331},
        {'range': 'Hard', 'start': 332, 'end': 544}
    ]

    start = 1
    end = 1
    for r in diff_ranges:
        if difficulty == r['range']:
            start = r['start']
            end = r['end']

    random_ids = [random.randint(start, end) for i in range(10)]

    word_dict_list = get_word_rows(random_ids)
    return word_dict_list


def selected_word(word, diff_level):
    print(word, diff_level)
    # store word and points value in db


def sent_sketch(data):
    data['created_at'] = datetime.now().strftime("%d %b, %H:%M")
    save_sketch(data['room'], data['url'], data['user_id'], data['created_at'])