from voip import create_app, socketio

app = create_app()



if __name__ == '__main__':
    # socketio.run(app, debug=True)
    app.run(host='0.0.0.0', port=80, debug=True)