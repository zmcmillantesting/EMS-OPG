# Flask HTTP Reference

## 1. HTTP Methods

HTTP methods tell Flask **what type of action the client is requesting**.

| Method   | Purpose               | Example                  |
| -------- | --------------------- | ------------------------ |
| `GET`    | Retrieve data         | Get a list of devices    |
| `POST`   | Create/send data      | Create a new device      |
| `PUT`    | Replace/update data   | Replace a device         |
| `PATCH`  | Partially update data | Update a device's status |
| `DELETE` | Delete data           | Delete a device          |

### Flask Example

```python
@app.route("/devices", methods=["GET"])
def get_devices():
    return "Getting devices"
```

Multiple methods can be allowed:

```python
@app.route("/devices", methods=["GET", "POST"])
def devices():
    if request.method == "GET":
        return "Getting devices"

    if request.method == "POST":
        return "Creating device"
```

---

# 2. HTTP Status Codes

HTTP status codes tell the client **what happened with the request**.

### 2xx — Success

|  Code | Meaning    | Typical Use                             |
| ----: | ---------- | --------------------------------------- |
| `200` | OK         | Request succeeded                       |
| `201` | Created    | New resource was created                |
| `204` | No Content | Request succeeded with no response body |

Example:

```python
return "Device found", 200
```

---

### 4xx — Client Error

|  Code | Meaning            | Typical Use                          |
| ----: | ------------------ | ------------------------------------ |
| `400` | Bad Request        | Invalid/missing input                |
| `401` | Unauthorized       | Authentication required              |
| `403` | Forbidden          | Client is not allowed                |
| `404` | Not Found          | Resource does not exist              |
| `405` | Method Not Allowed | HTTP method isn't supported          |
| `409` | Conflict           | Request conflicts with existing data |

Example:

```python
return "Device not found", 404
```

---

### 5xx — Server Error

|  Code | Meaning               | Typical Use                               |
| ----: | --------------------- | ----------------------------------------- |
| `500` | Internal Server Error | Unexpected server-side error              |
| `502` | Bad Gateway           | Problem communicating with another server |
| `503` | Service Unavailable   | Server/service temporarily unavailable    |

Example:

```python
return "Internal server error", 500
```

---

# 3. Custom Response Status

Flask allows you to return a response **and explicitly specify its HTTP status code**.

The basic syntax is:

```python
return response, status_code
```

Example:

```python
return "Created", 201
```

Here:

* `"Created"` = response body
* `201` = HTTP status code

---

## JSON Response With Status Code

```python
from flask import jsonify

return jsonify({
    "message": "Device created"
}), 201
```

The client receives:

```http
HTTP/1.1 201
```

with:

```json
{
    "message": "Device created"
}
```

---

# 4. Common Flask Patterns

### Successful request

```python
return "Success", 200
```

### Resource created

```python
return "Device created", 201
```

### Invalid input

```python
return "Invalid request", 400
```

### Not authorized

```python
return "Unauthorized", 401
```

### Forbidden

```python
return "Forbidden", 403
```

### Resource not found

```python
return "Device not found", 404
```

### Conflict

```python
return "Device already exists", 409
```

### Server error

```python
return "Internal server error", 500
```

---

# 5. Typical REST API Pattern

For an API dealing with devices:

```text
GET     /devices
POST    /devices
GET     /devices/<id>
PUT     /devices/<id>
PATCH   /devices/<id>
DELETE  /devices/<id>
```

Typical responses:

```text
GET /devices
    → 200 OK

POST /devices
    → 201 Created

GET /devices/123
    → 200 OK
    → 404 Not Found

PUT /devices/123
    → 200 OK
    → 404 Not Found

PATCH /devices/123
    → 200 OK
    → 404 Not Found

DELETE /devices/123
    → 204 No Content
    → 404 Not Found
```

---

# 6. Easy Way to Remember

### Methods = What are you trying to do?

```text
GET     → Get
POST    → Create
PUT     → Replace
PATCH   → Modify
DELETE  → Delete
```

### Status codes = What happened?

```text
2xx → Success
4xx → Client made a bad/invalid request
5xx → Server had a problem
```

The most important Flask combination to remember is:

```python
return response, status_code
```

For example:

```python
return jsonify({"error": "Device not found"}), 404
```
