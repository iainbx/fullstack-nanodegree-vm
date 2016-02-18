from catalog import app

app.secret_key = "asecret"
app.debug = True
app.run(host='0.0.0.0', port=8000)