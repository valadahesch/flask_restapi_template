$(function () {
	// Handler for .ready() called.

	var status = $("#status"),
		waiter = $("#waiter"),
		style = {},
		DISCONNECTED = 0,
		CONNECTING = 1,
		CONNECTED = 2,
		state = DISCONNECTED,
		curren_user = "",
		title_element = document.querySelector("title");

	function tac_connect() {
		waiter.show();
		state = CONNECTING;
		title_element.text = "[认证中]" + "@" + document.domain;
		$.ajax({
			url: "/service/user/current",
			dataType: "json",
			type: "GET",
			success: function (req) {
				curren_user = req.data.display_name;
				title_element.text = "[连接中]" + curren_user + "@" + document.domain;
				$.ajax({
					url:
						"/worker?key=" +
						document.domain.replace(".demo.hillstonenet.com", ""),
					type: "get",
					complete: ajax_complete_callback,
				});
			},
			error: function (err) {
				title_element.text = "[认证失败]" + "@" + document.domain;
				log_status(error.status);
			},
		});
	}

	function log_status(text) {
		console.log(text);
		status.html(text.split("\n").join("<br/>"));
	}

	function ajax_complete_callback(resp) {
		if (resp.status !== 200) {
			log_status(resp.status + ": " + resp.statusText);
			state = DISCONNECTED;
			return;
		}

		var msg = resp.responseJSON;
		if (!msg.id) {
			log_status(msg.status);
			state = DISCONNECTED;
			return;
		}
		var ws_url = window.location.href.split(/\?|#/, 1)[0].replace("http", "ws"),
			join = ws_url[ws_url.length - 1] === "/" ? "" : "/",
			url = "wss://" + document.domain + "/ws?id=" + msg.id,
			sock = new WebSocket(url),
			encoding = "utf-8",
			decoder = window.TextDecoder
				? new window.TextDecoder(encoding)
				: encoding,
			terminal = document.getElementById("terminal"),
			term = new Terminal({
				cursorBlink: true,
				theme: {
					foreground: "#00ff00",
					background: "black",
				},
			});
		//var attachAddon = new AttachAddon(sock);

		var attachAddon = new AttachAddon.AttachAddon(sock);
		var fitAddon = new FitAddon.FitAddon();
		term.loadAddon(attachAddon);
		term.loadAddon(fitAddon);

		sock.onopen = function () {
			waiter.hide();
			term.open(terminal);
			toggle_fullscreen(term);
			// update_font_family(term);
			term.focus();
			state = CONNECTED;

			term.write(
				curren_user +
					",欢迎访问demo站点，您的所有操作将被记录，还请规范使用demo设备。\r\n"
			);
			title_element.text = "[已连接]" + curren_user + "@" + document.domain;

			term.onData(function (data) {
				if (state === CONNECTED) {
					sock.send(
						JSON.stringify({
							data: data,
						})
					);
				} else {
					term.dispose();
					tac_connect();
				}
			});

			term.onResize = function (cols, rows) {
				if (cols !== this.cols || rows !== this.rows) {
					console.log(
						"Resizing terminal to geometry: " + format_geometry(cols, rows)
					);
					this.resize(cols, rows);
					sock.send(
						JSON.stringify({
							resize: [cols, rows],
						})
					);
				}
			};
		};

		sock.onerror = function (e) {
			console.error(e);
		};

		sock.onclose = function (e) {
			term.write(e.reason);
			state = DISCONNECTED;
			title_element.text = "[已断开]" + curren_user + "@" + document.domain;
		};

		$(window).resize(function () {
			if (term) {
				resize_terminal(term);
			}
		});

		function toggle_fullscreen(term) {
			$("#terminal .terminal").toggleClass("fullscreen");
			resize_terminal(term);
			//fitAddon.fit();
		}

		function resize_terminal(term) {
			var geometry = current_geometry(term);
			term.resize(geometry.cols, geometry.rows);
		}

		function current_geometry(term) {
			if (!style.width || !style.height) {
				try {
					get_cell_size(term);
				} catch (TypeError) {
					parse_xterm_style();
				}
			}

			var cols = parseInt(window.innerWidth / style.width, 10) - 1;
			var rows = parseInt(window.innerHeight / style.height, 10);
			return {
				cols: cols,
				rows: rows,
			};
		}

		function get_cell_size(term) {
			style.width =
				term._core._renderService._renderer.dimensions.actualCellWidth;
			style.height =
				term._core._renderService._renderer.dimensions.actualCellHeight;
		}

		function parse_xterm_style() {
			var text = $(".xterm-helpers style").text();
			var arr = text.split("xterm-normal-char{width:");
			style.width = parseFloat(arr[1]);
			arr = text.split("div{height:");
			style.height = parseFloat(arr[1]);
		}

		// Attach the socket to term
		//term.loadAddon(attachAddon);
	}
	tac_connect();
});
