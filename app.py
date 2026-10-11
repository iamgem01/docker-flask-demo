
import base64
import io

import qrcode
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Studio</title>
    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            background: #f3f7f4;
            color: #183b2b;
            display: grid;
            place-items: center;
            padding: 24px;
        }

        .container {
            width: 100%;
            max-width: 520px;
            background: white;
            border-radius: 20px;
            padding: 32px;
            box-shadow: 0 12px 40px #173b2b12;
        }

        .brand {
            color: #258454;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        h1 { margin-bottom: 8px; }
        .subtitle { color: #6b7d73; line-height: 1.6; }

        label {
            display: block;
            font-weight: bold;
            margin: 24px 0 8px;
        }

        textarea {
            width: 100%;
            min-height: 120px;
            padding: 14px;
            border: 1px solid #d6e2da;
            border-radius: 10px;
            font: inherit;
            resize: vertical;
        }

        textarea:focus {
            outline: 2px solid #79c99a;
            border-color: transparent;
        }

        button, .download {
            display: block;
            width: 100%;
            padding: 14px;
            margin-top: 14px;
            border: none;
            border-radius: 10px;
            background: #217a4b;
            color: white;
            font-size: 15px;
            font-weight: bold;
            text-align: center;
            text-decoration: none;
            cursor: pointer;
        }

        button:hover, .download:hover { background: #185f39; }

        .error {
            background: #fff0f0;
            color: #a32121;
            padding: 12px;
            border-radius: 8px;
            margin-top: 16px;
        }

        .result {
            margin-top: 26px;
            padding-top: 22px;
            border-top: 1px solid #e6eee8;
            text-align: center;
        }

        .qr-image {
            display: block;
            width: min(100%, 280px);
            height: auto;
            margin: 18px auto;
            image-rendering: pixelated;
        }

        .hint { color: #6b7d73; font-size: 13px; }
        footer { margin-top: 24px; text-align: center; color: #829087; font-size: 12px; }
    </style>
</head>
<body>
    <main class="container">
        <div class="brand">QR STUDIO</div>
        <h1>Tạo mã QR của bạn</h1>
        <p class="subtitle">
            Biến văn bản hoặc đường link thành mã QR chỉ trong vài giây.
        </p>

        <form method="POST" action="/qr">
            <label for="content">Nội dung hoặc URL</label>
            <textarea id="content" name="content"
                maxlength="2000" required
                placeholder="Ví dụ: https://github.com/iamgem01/docker-flask-demo">{{ content }}</textarea>
            <button type="submit">Tạo mã QR</button>
        </form>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        {% if qr_data %}
            <section class="result">
                <h2>Mã QR của bạn đã sẵn sàng!</h2>
                <img class="qr-image" src="{{ qr_data }}" alt="Mã QR đã tạo">
                <a class="download" href="{{ qr_data }}"
                   download="my-qr-code.png">Tải ảnh PNG</a>
                <p class="hint">Dùng camera điện thoại để quét thử nhé.</p>
            </section>
        {% endif %}

        <footer>QR Studio · Powered by Flask & Docker</footer>
    </main>
</body>
</html>
"""


@app.get("/")
def home():
    return jsonify({
        "message": "Hello from Docker!",
        "status": "running"
    })


@app.get("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/qr", methods=["GET", "POST"])
def qr_generator():
    content = ""
    qr_data = None
    error = None

    if request.method == "POST":
        content = request.form.get("content", "").strip()

        if not content:
            error = "Vui lòng nhập nội dung trước khi tạo mã QR."
        elif len(content) > 2000:
            error = "Nội dung vượt quá giới hạn 2000 ký tự."
        else:
            try:
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(content)
                qr.make(fit=True)

                image = qr.make_image(
                    fill_color="black",
                    back_color="white"
                )

                buffer = io.BytesIO()
                image.save(buffer, format="PNG")

                encoded_image = base64.b64encode(
                    buffer.getvalue()
                ).decode("ascii")

                qr_data = f"data:image/png;base64,{encoded_image}"

            except Exception:
                app.logger.exception("QR generation failed")
                error = "Không thể tạo mã QR. Vui lòng thử nội dung khác."

    return render_template_string(
        HTML_TEMPLATE,
        content=content,
        qr_data=qr_data,
        error=error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
