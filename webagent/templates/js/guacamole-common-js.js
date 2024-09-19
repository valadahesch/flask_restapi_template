/**
 * Bundled by jsDelivr using Rollup v2.79.1 and Terser v5.19.2.
 * Original file: /npm/guacamole-common-js@1.5.0/dist/esm/guacamole-common.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
var e;
((e = e || {}).ArrayBufferReader = function (e) {
	var t = this;
	(e.onblob = function (e) {
		for (
			var n = window.atob(e),
				i = new ArrayBuffer(n.length),
				r = new Uint8Array(i),
				o = 0;
			o < n.length;
			o++
		)
			r[o] = n.charCodeAt(o);
		t.ondata && t.ondata(i);
	}),
		(e.onend = function () {
			t.onend && t.onend();
		}),
		(this.ondata = null),
		(this.onend = null);
}),
	((e = e || {}).ArrayBufferWriter = function (t) {
		var n = this;
		function i(e) {
			for (var n = "", i = 0; i < e.byteLength; i++)
				n += String.fromCharCode(e[i]);
			t.sendBlob(window.btoa(n));
		}
		(t.onack = function (e) {
			n.onack && n.onack(e);
		}),
			(this.blobLength = e.ArrayBufferWriter.DEFAULT_BLOB_LENGTH),
			(this.sendData = function (e) {
				var t = new Uint8Array(e);
				if (t.length <= n.blobLength) i(t);
				else
					for (var r = 0; r < t.length; r += n.blobLength)
						i(t.subarray(r, r + n.blobLength));
			}),
			(this.sendEnd = function () {
				t.sendEnd();
			}),
			(this.onack = null);
	}),
	(e.ArrayBufferWriter.DEFAULT_BLOB_LENGTH = 6048),
	((e = e || {}).AudioContextFactory = {
		singleton: null,
		getAudioContext: function () {
			var t = window.AudioContext || window.webkitAudioContext;
			if (t)
				try {
					return (
						e.AudioContextFactory.singleton ||
							(e.AudioContextFactory.singleton = new t()),
						e.AudioContextFactory.singleton
					);
				} catch (e) {}
			return null;
		},
	}),
	((e = e || {}).AudioPlayer = function () {
		this.sync = function () {};
	}),
	(e.AudioPlayer.isSupportedType = function (t) {
		return e.RawAudioPlayer.isSupportedType(t);
	}),
	(e.AudioPlayer.getSupportedTypes = function () {
		return e.RawAudioPlayer.getSupportedTypes();
	}),
	(e.AudioPlayer.getInstance = function (t, n) {
		return e.RawAudioPlayer.isSupportedType(n)
			? new e.RawAudioPlayer(t, n)
			: null;
	}),
	(e.RawAudioPlayer = function (t, n) {
		var i = e.RawAudioFormat.parse(n),
			r = e.AudioContextFactory.getAudioContext(),
			o = r.currentTime,
			a = new e.ArrayBufferReader(t),
			s = 1 === i.bytesPerSample ? window.Int8Array : window.Int16Array,
			u = 1 === i.bytesPerSample ? 128 : 32768,
			l = [],
			c = function () {
				var e = (function (e) {
					if (e.length <= 1) return e[0];
					var t = 0;
					e.forEach(function (e) {
						t += e.length;
					});
					var n = 0,
						i = new s(t);
					return (
						e.forEach(function (e) {
							i.set(e, n), (n += e.length);
						}),
						i
					);
				})(l);
				return e
					? ((l = (function (e) {
							for (
								var t = Number.MAX_VALUE,
									n = e.length,
									r = Math.floor(e.length / i.channels),
									o = Math.floor(0.02 * i.rate),
									a = Math.max(i.channels * o, i.channels * (r - o));
								a < e.length;
								a += i.channels
							) {
								for (var u = 0, l = 0; l < i.channels; l++)
									u += Math.abs(e[a + l]);
								u <= t && ((n = a + i.channels), (t = u));
							}
							return n === e.length
								? [e]
								: [
										new s(e.buffer.slice(0, n * i.bytesPerSample)),
										new s(e.buffer.slice(n * i.bytesPerSample)),
								  ];
					  })(e)),
					  (e = l.shift()))
					: null;
			};
		(a.ondata = function (e) {
			!(function (e) {
				l.push(new s(e));
			})(new s(e));
			var t = c();
			if (t) {
				var n = r.currentTime;
				o < n && (o = n);
				var a = r.createBufferSource();
				a.connect(r.destination),
					a.start || (a.start = a.noteOn),
					(a.buffer = (function (e) {
						var t = e.length / i.channels,
							n = r.currentTime;
						o < n && (o = n);
						for (
							var a = r.createBuffer(i.channels, t, i.rate), s = 0;
							s < i.channels;
							s++
						)
							for (var l = a.getChannelData(s), c = s, h = 0; h < t; h++)
								(l[h] = e[c] / u), (c += i.channels);
						return a;
					})(t)),
					a.start(o),
					(o += t.length / i.channels / i.rate);
			}
		}),
			(this.sync = function () {
				var e = r.currentTime;
				o = Math.min(o, e + 0.3);
			});
	}),
	(e.RawAudioPlayer.prototype = new e.AudioPlayer()),
	(e.RawAudioPlayer.isSupportedType = function (t) {
		return (
			!!e.AudioContextFactory.getAudioContext() &&
			null !== e.RawAudioFormat.parse(t)
		);
	}),
	(e.RawAudioPlayer.getSupportedTypes = function () {
		return e.AudioContextFactory.getAudioContext()
			? ["audio/L8", "audio/L16"]
			: [];
	}),
	((e = e || {}).AudioRecorder = function () {
		(this.onclose = null), (this.onerror = null);
	}),
	(e.AudioRecorder.isSupportedType = function (t) {
		return e.RawAudioRecorder.isSupportedType(t);
	}),
	(e.AudioRecorder.getSupportedTypes = function () {
		return e.RawAudioRecorder.getSupportedTypes();
	}),
	(e.AudioRecorder.getInstance = function (t, n) {
		return e.RawAudioRecorder.isSupportedType(n)
			? new e.RawAudioRecorder(t, n)
			: null;
	}),
	(e.RawAudioRecorder = function (t, n) {
		var i = this,
			r = e.RawAudioFormat.parse(n),
			o = e.AudioContextFactory.getAudioContext();
		navigator.mediaDevices || (navigator.mediaDevices = {}),
			navigator.mediaDevices.getUserMedia ||
				(navigator.mediaDevices.getUserMedia = (
					navigator.getUserMedia ||
					navigator.webkitGetUserMedia ||
					navigator.mozGetUserMedia ||
					navigator.msGetUserMedia
				).bind(navigator));
		var a = new e.ArrayBufferWriter(t),
			s = 1 === r.bytesPerSample ? window.Int8Array : window.Int16Array,
			u = 1 === r.bytesPerSample ? 128 : 32768,
			l = 0,
			c = 0,
			h = null,
			d = null,
			f = null,
			p = function (e) {
				if (0 === e) return 1;
				var t = Math.PI * e;
				return Math.sin(t) / t;
			},
			v = function (e, t) {
				for (
					var n,
						i,
						r = (e.length - 1) * t,
						o = Math.floor(r) - 3 + 1,
						a = Math.floor(r) + 3,
						s = 0,
						u = o;
					u <= a;
					u++
				)
					s +=
						(e[u] || 0) *
						(-(i = 3) < (n = r - u) && n < i ? p(n) * p(n / i) : 0);
				return s;
			},
			g = function (e) {
				(f = o.createScriptProcessor(2048, r.channels, r.channels)).connect(
					o.destination
				),
					(f.onaudioprocess = function (e) {
						a.sendData(
							(function (e) {
								var t = e.length;
								l += t;
								var n = Math.round((l * r.rate) / e.sampleRate) - c;
								c += n;
								for (var i = new s(n * r.channels), o = 0; o < r.channels; o++)
									for (var a = e.getChannelData(o), h = o, d = 0; d < n; d++)
										(i[h] = v(a, d / (n - 1)) * u), (h += r.channels);
								return i;
							})(e.inputBuffer).buffer
						);
					}),
					(d = o.createMediaStreamSource(e)).connect(f),
					"suspended" === o.state && o.resume(),
					(h = e);
			},
			m = function () {
				a.sendEnd(), i.onerror && i.onerror();
			};
		a.onack = function (t) {
			var n;
			t.code !== e.Status.Code.SUCCESS || h
				? (!(function () {
						if ((d && d.disconnect(), f && f.disconnect(), h))
							for (var e = h.getTracks(), t = 0; t < e.length; t++) e[t].stop();
						(f = null), (d = null), (h = null), a.sendEnd();
				  })(),
				  (a.onack = null),
				  t.code === e.Status.Code.RESOURCE_CLOSED
						? i.onclose && i.onclose()
						: i.onerror && i.onerror())
				: (n = navigator.mediaDevices.getUserMedia({ audio: !0 }, g, m)) &&
				  n.then &&
				  n.then(g, m);
		};
	}),
	(e.RawAudioRecorder.prototype = new e.AudioRecorder()),
	(e.RawAudioRecorder.isSupportedType = function (t) {
		return (
			!!e.AudioContextFactory.getAudioContext() &&
			null !== e.RawAudioFormat.parse(t)
		);
	}),
	(e.RawAudioRecorder.getSupportedTypes = function () {
		return e.AudioContextFactory.getAudioContext()
			? ["audio/L8", "audio/L16"]
			: [];
	}),
	((e = e || {}).BlobReader = function (e, t) {
		var n,
			i = this,
			r = 0;
		(n = window.BlobBuilder
			? new BlobBuilder()
			: window.WebKitBlobBuilder
			? new WebKitBlobBuilder()
			: window.MozBlobBuilder
			? new MozBlobBuilder()
			: new (function () {
					var e = [];
					(this.append = function (n) {
						e.push(new Blob([n], { type: t }));
					}),
						(this.getBlob = function () {
							return new Blob(e, { type: t });
						});
			  })()),
			(e.onblob = function (t) {
				for (
					var o = window.atob(t),
						a = new ArrayBuffer(o.length),
						s = new Uint8Array(a),
						u = 0;
					u < o.length;
					u++
				)
					s[u] = o.charCodeAt(u);
				n.append(a),
					(r += a.byteLength),
					i.onprogress && i.onprogress(a.byteLength),
					e.sendAck("OK", 0);
			}),
			(e.onend = function () {
				i.onend && i.onend();
			}),
			(this.getLength = function () {
				return r;
			}),
			(this.getBlob = function () {
				return n.getBlob();
			}),
			(this.onprogress = null),
			(this.onend = null);
	}),
	((e = e || {}).BlobWriter = function (t) {
		var n = this,
			i = new e.ArrayBufferWriter(t);
		i.onack = function (e) {
			n.onack && n.onack(e);
		};
		(this.sendBlob = function (e) {
			var t = 0,
				r = new FileReader(),
				o = function () {
					if (t >= e.size) n.oncomplete && n.oncomplete(e);
					else {
						var o = (function (e, t, n) {
							var i = (e.slice || e.webkitSlice || e.mozSlice).bind(e),
								r = n - t;
							if (r !== n) {
								var o = i(t, r);
								if (o.size === r) return o;
							}
							return i(t, n);
						})(e, t, t + i.blobLength);
						(t += i.blobLength), r.readAsArrayBuffer(o);
					}
				};
			(r.onload = function () {
				i.sendData(r.result),
					(i.onack = function (r) {
						n.onack && n.onack(r),
							r.isError() ||
								(n.onprogress && n.onprogress(e, t - i.blobLength), o());
					});
			}),
				(r.onerror = function () {
					n.onerror && n.onerror(e, t, r.error);
				}),
				o();
		}),
			(this.sendEnd = function () {
				i.sendEnd();
			}),
			(this.onack = null),
			(this.onerror = null),
			(this.onprogress = null),
			(this.oncomplete = null);
	}),
	((e = e || {}).Client = function (t) {
		var n = this,
			i = e.Client.State.IDLE,
			r = 0,
			o = null,
			a = 0,
			s = { 0: "butt", 1: "round", 2: "square" },
			u = { 0: "bevel", 1: "miter", 2: "round" },
			l = new e.Display(),
			c = {},
			h = {},
			d = [],
			f = [],
			p = [],
			v = new e.IntegerPool(),
			g = [];
		function m(e) {
			e != i && ((i = e), n.onstatechange && n.onstatechange(i));
		}
		function y() {
			return i == e.Client.State.CONNECTED || i == e.Client.State.WAITING;
		}
		(this.exportState = function (e) {
			var t = { currentState: i, currentTimestamp: r, layers: {} },
				n = {};
			for (var o in c) n[o] = c[o];
			l.flush(function () {
				for (var i in n) {
					var r = parseInt(i),
						o = n[i],
						a = o.toCanvas(),
						s = { width: o.width, height: o.height };
					o.width && o.height && (s.url = a.toDataURL("image/png")),
						r > 0 &&
							((s.x = o.x),
							(s.y = o.y),
							(s.z = o.z),
							(s.alpha = o.alpha),
							(s.matrix = o.matrix),
							(s.parent = S(o.parent))),
						(t.layers[i] = s);
				}
				e(t);
			});
		}),
			(this.importState = function (t, n) {
				var o, a;
				for (o in ((i = t.currentState),
				(r = t.currentTimestamp),
				l.cancel(),
				c))
					(a = parseInt(o)) > 0 && c[o].dispose();
				for (o in ((c = {}), t.layers)) {
					a = parseInt(o);
					var s = t.layers[o],
						u = w(a);
					if (
						(l.resize(u, s.width, s.height),
						s.url && (l.setChannelMask(u, e.Layer.SRC), l.draw(u, 0, 0, s.url)),
						a > 0 && s.parent >= 0)
					) {
						var h = w(s.parent);
						l.move(u, h, s.x, s.y, s.z), l.shade(u, s.alpha);
						var d = s.matrix;
						l.distort(u, d[0], d[1], d[2], d[3], d[4], d[5]);
					}
				}
				l.flush(n);
			}),
			(this.getDisplay = function () {
				return l;
			}),
			(this.sendSize = function (e, n) {
				y() && t.sendMessage("size", e, n);
			}),
			(this.sendKeyEvent = function (e, n) {
				y() && t.sendMessage("key", n, e);
			}),
			(this.sendMouseState = function (e, n) {
				if (y()) {
					var i = e.x,
						r = e.y;
					n && ((i /= l.getScale()), (r /= l.getScale())),
						l.moveCursor(Math.floor(i), Math.floor(r));
					var o = 0;
					e.left && (o |= 1),
						e.middle && (o |= 2),
						e.right && (o |= 4),
						e.up && (o |= 8),
						e.down && (o |= 16),
						t.sendMessage("mouse", Math.floor(i), Math.floor(r), o);
				}
			}),
			(this.sendTouchState = function (e, n) {
				if (y()) {
					var i = e.x,
						r = e.y;
					n && ((i /= l.getScale()), (r /= l.getScale())),
						t.sendMessage(
							"touch",
							e.id,
							Math.floor(i),
							Math.floor(r),
							Math.floor(e.radiusX),
							Math.floor(e.radiusY),
							e.angle,
							e.force
						);
				}
			}),
			(this.createOutputStream = function () {
				var t = v.next();
				return (g[t] = new e.OutputStream(n, t));
			}),
			(this.createAudioStream = function (e) {
				var i = n.createOutputStream();
				return t.sendMessage("audio", i.index, e), i;
			}),
			(this.createFileStream = function (e, i) {
				var r = n.createOutputStream();
				return t.sendMessage("file", r.index, e, i), r;
			}),
			(this.createPipeStream = function (e, i) {
				var r = n.createOutputStream();
				return t.sendMessage("pipe", r.index, e, i), r;
			}),
			(this.createClipboardStream = function (e) {
				var i = n.createOutputStream();
				return t.sendMessage("clipboard", i.index, e), i;
			}),
			(this.createArgumentValueStream = function (e, i) {
				var r = n.createOutputStream();
				return t.sendMessage("argv", r.index, e, i), r;
			}),
			(this.createObjectOutputStream = function (e, i, r) {
				var o = n.createOutputStream();
				return t.sendMessage("put", e, o.index, i, r), o;
			}),
			(this.requestObjectInputStream = function (e, n) {
				y() && t.sendMessage("get", e, n);
			}),
			(this.sendAck = function (e, n, i) {
				y() && t.sendMessage("ack", e, n, i);
			}),
			(this.sendBlob = function (e, n) {
				y() && t.sendMessage("blob", e, n);
			}),
			(this.endStream = function (e) {
				y() && (t.sendMessage("end", e), g[e] && (v.free(e), delete g[e]));
			}),
			(this.onstatechange = null),
			(this.onname = null),
			(this.onerror = null),
			(this.onmsg = null),
			(this.onjoin = null),
			(this.onleave = null),
			(this.onaudio = null),
			(this.onvideo = null),
			(this.onmultitouch = null),
			(this.onargv = null),
			(this.onclipboard = null),
			(this.onfile = null),
			(this.onfilesystem = null),
			(this.onpipe = null),
			(this.onrequired = null),
			(this.onsync = null);
		var w = function (e) {
				var t = c[e];
				return (
					t ||
						((t =
							0 === e
								? l.getDefaultLayer()
								: e > 0
								? l.createLayer()
								: l.createBuffer()),
						(c[e] = t)),
					t
				);
			},
			S = function (e) {
				if (!e) return null;
				for (var t in c) if (e === c[t]) return parseInt(t);
				return null;
			};
		var T = {
				"miter-limit": function (e, t) {
					l.setMiterLimit(e, parseFloat(t));
				},
				"multi-touch": function (t, i) {
					n.onmultitouch &&
						t instanceof e.Display.VisibleLayer &&
						n.onmultitouch(t, parseInt(i));
				},
			},
			E = {
				ack: function (t) {
					var n = parseInt(t[0]),
						i = t[1],
						r = parseInt(t[2]),
						o = g[n];
					o &&
						(o.onack && o.onack(new e.Status(r, i)),
						r >= 256 && g[n] === o && (v.free(n), delete g[n]));
				},
				arc: function (e) {
					var t = w(parseInt(e[0])),
						n = parseInt(e[1]),
						i = parseInt(e[2]),
						r = parseInt(e[3]),
						o = parseFloat(e[4]),
						a = parseFloat(e[5]),
						s = parseInt(e[6]);
					l.arc(t, n, i, r, o, a, 0 != s);
				},
				argv: function (t) {
					var i = parseInt(t[0]),
						r = t[1],
						o = t[2];
					if (n.onargv) {
						var a = (f[i] = new e.InputStream(n, i));
						n.onargv(a, r, o);
					} else n.sendAck(i, "Receiving argument values unsupported", 256);
				},
				audio: function (t) {
					var i = parseInt(t[0]),
						r = t[1],
						o = (f[i] = new e.InputStream(n, i)),
						a = null;
					n.onaudio && (a = n.onaudio(o, r)),
						a || (a = e.AudioPlayer.getInstance(o, r)),
						a
							? ((h[i] = a), n.sendAck(i, "OK", 0))
							: n.sendAck(i, "BAD TYPE", 783);
				},
				blob: function (e) {
					var t = parseInt(e[0]),
						n = e[1],
						i = f[t];
					i && i.onblob && i.onblob(n);
				},
				body: function (t) {
					var i = parseInt(t[0]),
						r = p[i],
						o = parseInt(t[1]),
						a = t[2],
						s = t[3];
					if (r && r.onbody) {
						var u = (f[o] = new e.InputStream(n, o));
						r.onbody(u, a, s);
					} else n.sendAck(o, "Receipt of body unsupported", 256);
				},
				cfill: function (e) {
					var t = parseInt(e[0]),
						n = w(parseInt(e[1])),
						i = parseInt(e[2]),
						r = parseInt(e[3]),
						o = parseInt(e[4]),
						a = parseInt(e[5]);
					l.setChannelMask(n, t), l.fillColor(n, i, r, o, a);
				},
				clip: function (e) {
					var t = w(parseInt(e[0]));
					l.clip(t);
				},
				clipboard: function (t) {
					var i = parseInt(t[0]),
						r = t[1];
					if (n.onclipboard) {
						var o = (f[i] = new e.InputStream(n, i));
						n.onclipboard(o, r);
					} else n.sendAck(i, "Clipboard unsupported", 256);
				},
				close: function (e) {
					var t = w(parseInt(e[0]));
					l.close(t);
				},
				copy: function (e) {
					var t = w(parseInt(e[0])),
						n = parseInt(e[1]),
						i = parseInt(e[2]),
						r = parseInt(e[3]),
						o = parseInt(e[4]),
						a = parseInt(e[5]),
						s = w(parseInt(e[6])),
						u = parseInt(e[7]),
						c = parseInt(e[8]);
					l.setChannelMask(s, a), l.copy(t, n, i, r, o, s, u, c);
				},
				cstroke: function (e) {
					var t = parseInt(e[0]),
						n = w(parseInt(e[1])),
						i = s[parseInt(e[2])],
						r = u[parseInt(e[3])],
						o = parseInt(e[4]),
						a = parseInt(e[5]),
						c = parseInt(e[6]),
						h = parseInt(e[7]),
						d = parseInt(e[8]);
					l.setChannelMask(n, t), l.strokeColor(n, i, r, o, a, c, h, d);
				},
				cursor: function (e) {
					var t = parseInt(e[0]),
						n = parseInt(e[1]),
						i = w(parseInt(e[2])),
						r = parseInt(e[3]),
						o = parseInt(e[4]),
						a = parseInt(e[5]),
						s = parseInt(e[6]);
					l.setCursor(t, n, i, r, o, a, s);
				},
				curve: function (e) {
					var t = w(parseInt(e[0])),
						n = parseInt(e[1]),
						i = parseInt(e[2]),
						r = parseInt(e[3]),
						o = parseInt(e[4]),
						a = parseInt(e[5]),
						s = parseInt(e[6]);
					l.curveTo(t, n, i, r, o, a, s);
				},
				disconnect: function (e) {
					n.disconnect();
				},
				dispose: function (e) {
					var t = parseInt(e[0]);
					if (t > 0) {
						var n = w(t);
						l.dispose(n), delete c[t];
					} else t < 0 && delete c[t];
				},
				distort: function (e) {
					var t = parseInt(e[0]),
						n = parseFloat(e[1]),
						i = parseFloat(e[2]),
						r = parseFloat(e[3]),
						o = parseFloat(e[4]),
						a = parseFloat(e[5]),
						s = parseFloat(e[6]);
					if (t >= 0) {
						var u = w(t);
						l.distort(u, n, i, r, o, a, s);
					}
				},
				error: function (t) {
					var i = t[0],
						r = parseInt(t[1]);
					n.onerror && n.onerror(new e.Status(r, i)), n.disconnect();
				},
				end: function (e) {
					var t = parseInt(e[0]),
						n = f[t];
					n && (n.onend && n.onend(), delete f[t]);
				},
				file: function (t) {
					var i = parseInt(t[0]),
						r = t[1],
						o = t[2];
					if (n.onfile) {
						var a = (f[i] = new e.InputStream(n, i));
						n.onfile(a, r, o);
					} else n.sendAck(i, "File transfer unsupported", 256);
				},
				filesystem: function (t) {
					var i = parseInt(t[0]),
						r = t[1];
					if (n.onfilesystem) {
						var o = (p[i] = new e.Object(n, i));
						n.onfilesystem(o, r);
					}
				},
				identity: function (e) {
					var t = w(parseInt(e[0]));
					l.setTransform(t, 1, 0, 0, 1, 0, 0);
				},
				img: function (t) {
					var i = parseInt(t[0]),
						r = parseInt(t[1]),
						o = w(parseInt(t[2])),
						a = t[3],
						s = parseInt(t[4]),
						u = parseInt(t[5]),
						c = (f[i] = new e.InputStream(n, i));
					l.setChannelMask(o, r), l.drawStream(o, s, u, c, a);
				},
				jpeg: function (e) {
					var t = parseInt(e[0]),
						n = w(parseInt(e[1])),
						i = parseInt(e[2]),
						r = parseInt(e[3]),
						o = e[4];
					l.setChannelMask(n, t),
						l.draw(n, i, r, "data:image/jpeg;base64," + o);
				},
				lfill: function (e) {
					var t = parseInt(e[0]),
						n = w(parseInt(e[1])),
						i = w(parseInt(e[2]));
					l.setChannelMask(n, t), l.fillLayer(n, i);
				},
				line: function (e) {
					var t = w(parseInt(e[0])),
						n = parseInt(e[1]),
						i = parseInt(e[2]);
					l.lineTo(t, n, i);
				},
				lstroke: function (e) {
					var t = parseInt(e[0]),
						n = w(parseInt(e[1])),
						i = w(parseInt(e[2]));
					l.setChannelMask(n, t), l.strokeLayer(n, i);
				},
				mouse: function (e) {
					var t = parseInt(e[0]),
						n = parseInt(e[1]);
					l.showCursor(!0), l.moveCursor(t, n);
				},
				move: function (e) {
					var t = parseInt(e[0]),
						n = parseInt(e[1]),
						i = parseInt(e[2]),
						r = parseInt(e[3]),
						o = parseInt(e[4]);
					if (t > 0 && n >= 0) {
						var a = w(t),
							s = w(n);
						l.move(a, s, i, r, o);
					}
				},
				msg: function (t) {
					var i,
						r,
						o = !0,
						a = parseInt(t[0]);
					if (
						(n.onmsg && void 0 === (o = n.onmsg(a, t.slice(1))) && (o = !0), o)
					)
						switch (a) {
							case e.Client.Message.USER_JOINED:
								(i = t[1]), (r = t[2]), n.onjoin && n.onjoin(i, r);
								break;
							case e.Client.Message.USER_LEFT:
								(i = t[1]), (r = t[2]), n.onleave && n.onleave(i, r);
						}
				},
				name: function (e) {
					n.onname && n.onname(e[0]);
				},
				nest: function (n) {
					(function (n) {
						var i = d[n];
						return (
							null == i &&
								((i = d[n] = new e.Parser()).oninstruction = t.oninstruction),
							i
						);
					})(parseInt(n[0])).receive(n[1]);
				},
				pipe: function (t) {
					var i = parseInt(t[0]),
						r = t[1],
						o = t[2];
					if (n.onpipe) {
						var a = (f[i] = new e.InputStream(n, i));
						n.onpipe(a, r, o);
					} else n.sendAck(i, "Named pipes unsupported", 256);
				},
				png: function (e) {
					var t = parseInt(e[0]),
						n = w(parseInt(e[1])),
						i = parseInt(e[2]),
						r = parseInt(e[3]),
						o = e[4];
					l.setChannelMask(n, t), l.draw(n, i, r, "data:image/png;base64," + o);
				},
				pop: function (e) {
					var t = w(parseInt(e[0]));
					l.pop(t);
				},
				push: function (e) {
					var t = w(parseInt(e[0]));
					l.push(t);
				},
				rect: function (e) {
					var t = w(parseInt(e[0])),
						n = parseInt(e[1]),
						i = parseInt(e[2]),
						r = parseInt(e[3]),
						o = parseInt(e[4]);
					l.rect(t, n, i, r, o);
				},
				required: function (e) {
					n.onrequired && n.onrequired(e);
				},
				reset: function (e) {
					var t = w(parseInt(e[0]));
					l.reset(t);
				},
				set: function (e) {
					var t = w(parseInt(e[0])),
						n = e[1],
						i = e[2],
						r = T[n];
					r && r(t, i);
				},
				shade: function (e) {
					var t = parseInt(e[0]),
						n = parseInt(e[1]);
					if (t >= 0) {
						var i = w(t);
						l.shade(i, n);
					}
				},
				size: function (e) {
					var t = parseInt(e[0]),
						n = w(t),
						i = parseInt(e[1]),
						r = parseInt(e[2]);
					l.resize(n, i, r);
				},
				start: function (e) {
					var t = w(parseInt(e[0])),
						n = parseInt(e[1]),
						i = parseInt(e[2]);
					l.moveTo(t, n, i);
				},
				sync: function (o) {
					var a = parseInt(o[0]),
						s = o[1] ? parseInt(o[1]) : 0;
					l.flush(
						function () {
							for (var e in h) {
								var n = h[e];
								n && n.sync();
							}
							a !== r && (t.sendMessage("sync", a), (r = a));
						},
						a,
						s
					),
						i === e.Client.State.WAITING && m(e.Client.State.CONNECTED),
						n.onsync && n.onsync(a, s);
				},
				transfer: function (t) {
					var n = w(parseInt(t[0])),
						i = parseInt(t[1]),
						r = parseInt(t[2]),
						o = parseInt(t[3]),
						a = parseInt(t[4]),
						s = parseInt(t[5]),
						u = w(parseInt(t[6])),
						c = parseInt(t[7]),
						h = parseInt(t[8]);
					3 === s
						? l.put(n, i, r, o, a, u, c, h)
						: 5 !== s &&
						  l.transfer(
								n,
								i,
								r,
								o,
								a,
								u,
								c,
								h,
								e.Client.DefaultTransferFunction[s]
						  );
				},
				transform: function (e) {
					var t = w(parseInt(e[0])),
						n = parseFloat(e[1]),
						i = parseFloat(e[2]),
						r = parseFloat(e[3]),
						o = parseFloat(e[4]),
						a = parseFloat(e[5]),
						s = parseFloat(e[6]);
					l.transform(t, n, i, r, o, a, s);
				},
				undefine: function (e) {
					var t = parseInt(e[0]),
						n = p[t];
					n && n.onundefine && n.onundefine();
				},
				video: function (t) {
					var i = parseInt(t[0]),
						r = w(parseInt(t[1])),
						o = t[2],
						a = (f[i] = new e.InputStream(n, i)),
						s = null;
					n.onvideo && (s = n.onvideo(a, r, o)),
						s || (s = e.VideoPlayer.getInstance(a, r, o)),
						s ? n.sendAck(i, "OK", 0) : n.sendAck(i, "BAD TYPE", 783);
				},
			},
			I = function () {
				t.sendMessage("nop"), (a = new Date().getTime());
			},
			b = function () {
				window.clearTimeout(o);
				var e = new Date().getTime(),
					t = Math.max(a + 5e3 - e, 0);
				t > 0 ? (o = window.setTimeout(I, t)) : I();
			};
		(t.oninstruction = function (e, t) {
			var n = E[e];
			n && n(t), b();
		}),
			(this.disconnect = function () {
				i != e.Client.State.DISCONNECTED &&
					i != e.Client.State.DISCONNECTING &&
					(m(e.Client.State.DISCONNECTING),
					window.clearTimeout(o),
					t.sendMessage("disconnect"),
					t.disconnect(),
					m(e.Client.State.DISCONNECTED));
			}),
			(this.connect = function (n) {
				m(e.Client.State.CONNECTING);
				try {
					t.connect(n);
				} catch (t) {
					throw (m(e.Client.State.IDLE), t);
				}
				b(), m(e.Client.State.WAITING);
			});
	}),
	(e.Client.State = {
		IDLE: 0,
		CONNECTING: 1,
		WAITING: 2,
		CONNECTED: 3,
		DISCONNECTING: 4,
		DISCONNECTED: 5,
	}),
	(e.Client.DefaultTransferFunction = {
		0: function (e, t) {
			t.red = t.green = t.blue = 0;
		},
		15: function (e, t) {
			t.red = t.green = t.blue = 255;
		},
		3: function (e, t) {
			(t.red = e.red),
				(t.green = e.green),
				(t.blue = e.blue),
				(t.alpha = e.alpha);
		},
		5: function (e, t) {},
		12: function (e, t) {
			(t.red = 255 & ~e.red),
				(t.green = 255 & ~e.green),
				(t.blue = 255 & ~e.blue),
				(t.alpha = e.alpha);
		},
		10: function (e, t) {
			(t.red = 255 & ~t.red),
				(t.green = 255 & ~t.green),
				(t.blue = 255 & ~t.blue);
		},
		1: function (e, t) {
			(t.red = e.red & t.red),
				(t.green = e.green & t.green),
				(t.blue = e.blue & t.blue);
		},
		14: function (e, t) {
			(t.red = 255 & ~(e.red & t.red)),
				(t.green = 255 & ~(e.green & t.green)),
				(t.blue = 255 & ~(e.blue & t.blue));
		},
		7: function (e, t) {
			(t.red = e.red | t.red),
				(t.green = e.green | t.green),
				(t.blue = e.blue | t.blue);
		},
		8: function (e, t) {
			(t.red = 255 & ~(e.red | t.red)),
				(t.green = 255 & ~(e.green | t.green)),
				(t.blue = 255 & ~(e.blue | t.blue));
		},
		6: function (e, t) {
			(t.red = e.red ^ t.red),
				(t.green = e.green ^ t.green),
				(t.blue = e.blue ^ t.blue);
		},
		9: function (e, t) {
			(t.red = 255 & ~(e.red ^ t.red)),
				(t.green = 255 & ~(e.green ^ t.green)),
				(t.blue = 255 & ~(e.blue ^ t.blue));
		},
		4: function (e, t) {
			(t.red = ~e.red & t.red & 255),
				(t.green = ~e.green & t.green & 255),
				(t.blue = ~e.blue & t.blue & 255);
		},
		13: function (e, t) {
			(t.red = 255 & (~e.red | t.red)),
				(t.green = 255 & (~e.green | t.green)),
				(t.blue = 255 & (~e.blue | t.blue));
		},
		2: function (e, t) {
			(t.red = e.red & ~t.red & 255),
				(t.green = e.green & ~t.green & 255),
				(t.blue = e.blue & ~t.blue & 255);
		},
		11: function (e, t) {
			(t.red = 255 & (e.red | ~t.red)),
				(t.green = 255 & (e.green | ~t.green)),
				(t.blue = 255 & (e.blue | ~t.blue));
		},
	}),
	(e.Client.Message = { USER_JOINED: 1, USER_LEFT: 2 }),
	((e = e || {}).DataURIReader = function (e, t) {
		var n = this,
			i = "data:" + t + ";base64,";
		(e.onblob = function (e) {
			i += e;
		}),
			(e.onend = function () {
				n.onend && n.onend();
			}),
			(this.getURI = function () {
				return i;
			}),
			(this.onend = null);
	}),
	((e = e || {}).Display = function () {
		var t = this,
			n = 0,
			i = 0,
			r = 1,
			o = document.createElement("div");
		(o.style.position = "relative"),
			(o.style.width = n + "px"),
			(o.style.height = i + "px"),
			(o.style.transformOrigin =
				o.style.webkitTransformOrigin =
				o.style.MozTransformOrigin =
				o.style.OTransformOrigin =
				o.style.msTransformOrigin =
					"0 0");
		var a = new e.Display.VisibleLayer(n, i),
			s = new e.Display.VisibleLayer(0, 0);
		s.setChannelMask(e.Layer.SRC),
			o.appendChild(a.getElement()),
			o.appendChild(s.getElement());
		var u = document.createElement("div");
		(u.style.position = "relative"),
			(u.style.width = n * r + "px"),
			(u.style.height = i * r + "px"),
			u.appendChild(o),
			(this.cursorHotspotX = 0),
			(this.cursorHotspotY = 0),
			(this.cursorX = 0),
			(this.cursorY = 0),
			(this.statisticWindow = 0),
			(this.onresize = null),
			(this.oncursor = null),
			(this.onstatistics = null);
		var l = [],
			c = [],
			h = null,
			d = function () {
				for (var e = 0, t = 0, n = 0, i = 0; i < c.length; ) {
					var r = c[i];
					if (!r.isReady()) break;
					r.flush(),
						(e = r.localTimestamp),
						(t = r.remoteTimestamp),
						(n += r.logicalFrames),
						i++;
				}
				c.splice(0, i), i && v(e, t, n);
			},
			f = function () {
				h ||
					(h = window.requestAnimationFrame(function e() {
						if (((h = null), c.length)) {
							if (c[0].isReady()) {
								var t = c.shift();
								t.flush(),
									v(t.localTimestamp, t.remoteTimestamp, t.logicalFrames);
							}
							c.length && (h = window.requestAnimationFrame(e));
						}
					}));
			},
			p = [],
			v = function (n, i, r) {
				if (t.statisticWindow) {
					for (
						var o = new Date().getTime(), a = 0;
						a < p.length && !(o - p[a].timestamp <= t.statisticWindow);
						a++
					);
					p.splice(0, a - 1),
						p.push({
							localTimestamp: n,
							remoteTimestamp: i,
							timestamp: o,
							frames: r,
						});
					var s = (p[p.length - 1].timestamp - p[0].timestamp) / 1e3,
						u = (p[p.length - 1].remoteTimestamp - p[0].remoteTimestamp) / 1e3,
						l = p.length,
						c = p.reduce(function (e, t) {
							return e + t.frames;
						}, 0),
						h = p.reduce(function (e, t) {
							return e + Math.max(0, t.frames - 1);
						}, 0),
						d = new e.Display.Statistics({
							processingLag: o - n,
							desktopFps: u && c ? c / u : null,
							clientFps: s ? l / s : null,
							serverFps: u ? l / u : null,
							dropRate: u ? h / u : null,
						});
					t.onstatistics && t.onstatistics(d);
				}
			};
		function g() {
			window.requestAnimationFrame && document.hasFocus() ? f() : d();
		}
		window.addEventListener(
			"blur",
			function () {
				h &&
					!document.hasFocus() &&
					(window.cancelAnimationFrame(h), (h = null), d());
			},
			!0
		);
		var m = function (e, t, n, i) {
			(this.localTimestamp = new Date().getTime()),
				(this.remoteTimestamp = n || this.localTimestamp),
				(this.logicalFrames = i || 0),
				(this.cancel = function () {
					(e = null),
						t.forEach(function (e) {
							e.cancel();
						}),
						(t = []);
				}),
				(this.isReady = function () {
					for (var e = 0; e < t.length; e++) if (t[e].blocked) return !1;
					return !0;
				}),
				(this.flush = function () {
					for (var n = 0; n < t.length; n++) t[n].execute();
					e && e();
				});
		};
		function y(e, t) {
			var n = this;
			(this.blocked = t),
				(this.cancel = function () {
					(n.blocked = !1), (e = null);
				}),
				(this.unblock = function () {
					n.blocked && ((n.blocked = !1), g());
				}),
				(this.execute = function () {
					e && e();
				});
		}
		function w(e, t) {
			var n = new y(e, t);
			return l.push(n), n;
		}
		(this.getElement = function () {
			return u;
		}),
			(this.getWidth = function () {
				return n;
			}),
			(this.getHeight = function () {
				return i;
			}),
			(this.getDefaultLayer = function () {
				return a;
			}),
			(this.getCursorLayer = function () {
				return s;
			}),
			(this.createLayer = function () {
				var t = new e.Display.VisibleLayer(n, i);
				return t.move(a, 0, 0, 0), t;
			}),
			(this.createBuffer = function () {
				var t = new e.Layer(0, 0);
				return (t.autosize = 1), t;
			}),
			(this.flush = function (e, t, n) {
				c.push(new m(e, l, t, n)), (l = []), g();
			}),
			(this.cancel = function () {
				c.forEach(function (e) {
					e.cancel();
				}),
					(c = []),
					l.forEach(function (e) {
						e.cancel();
					}),
					(l = []);
			}),
			(this.setCursor = function (e, n, i, r, o, a, u) {
				w(function () {
					(t.cursorHotspotX = e),
						(t.cursorHotspotY = n),
						s.resize(a, u),
						s.copy(i, r, o, a, u, 0, 0),
						t.moveCursor(t.cursorX, t.cursorY),
						t.oncursor && t.oncursor(s.toCanvas(), e, n);
				});
			}),
			(this.showCursor = function (e) {
				var t = s.getElement(),
					n = t.parentNode;
				!1 === e ? n && n.removeChild(t) : n !== o && o.appendChild(t);
			}),
			(this.moveCursor = function (e, n) {
				s.translate(e - t.cursorHotspotX, n - t.cursorHotspotY),
					(t.cursorX = e),
					(t.cursorY = n);
			}),
			(this.resize = function (e, s, l) {
				w(function () {
					e.resize(s, l),
						e === a &&
							((n = s),
							(i = l),
							(o.style.width = n + "px"),
							(o.style.height = i + "px"),
							(u.style.width = n * r + "px"),
							(u.style.height = i * r + "px"),
							t.onresize && t.onresize(s, l));
				});
			}),
			(this.drawImage = function (e, t, n, i) {
				w(function () {
					e.drawImage(t, n, i);
				});
			}),
			(this.drawBlob = function (e, t, n, i) {
				var r;
				if (window.createImageBitmap) {
					var o;
					(r = w(function () {
						e.drawImage(t, n, o);
					}, !0)),
						window.createImageBitmap(i).then(function (e) {
							(o = e), r.unblock();
						});
				} else {
					var a = URL.createObjectURL(i);
					r = w(function () {
						s.width && s.height && e.drawImage(t, n, s), URL.revokeObjectURL(a);
					}, !0);
					var s = new Image();
					(s.onload = r.unblock), (s.onerror = r.unblock), (s.src = a);
				}
			}),
			(this.drawStream = function (n, i, r, o, a) {
				var s;
				window.createImageBitmap
					? ((s = new e.BlobReader(o, a)).onend = function () {
							t.drawBlob(n, i, r, s.getBlob());
					  })
					: ((s = new e.DataURIReader(o, a)).onend = function () {
							t.draw(n, i, r, s.getURI());
					  });
			}),
			(this.draw = function (e, t, n, i) {
				var r = w(function () {
						o.width && o.height && e.drawImage(t, n, o);
					}, !0),
					o = new Image();
				(o.onload = r.unblock), (o.onerror = r.unblock), (o.src = i);
			}),
			(this.play = function (e, t, n, i) {
				var r = document.createElement("video");
				(r.type = t),
					(r.src = i),
					r.addEventListener(
						"play",
						function () {
							!(function t() {
								e.drawImage(0, 0, r), r.ended || window.setTimeout(t, 20);
							})();
						},
						!1
					),
					w(r.play);
			}),
			(this.transfer = function (e, t, n, i, r, o, a, s, u) {
				w(function () {
					o.transfer(e, t, n, i, r, a, s, u);
				});
			}),
			(this.put = function (e, t, n, i, r, o, a, s) {
				w(function () {
					o.put(e, t, n, i, r, a, s);
				});
			}),
			(this.copy = function (e, t, n, i, r, o, a, s) {
				w(function () {
					o.copy(e, t, n, i, r, a, s);
				});
			}),
			(this.moveTo = function (e, t, n) {
				w(function () {
					e.moveTo(t, n);
				});
			}),
			(this.lineTo = function (e, t, n) {
				w(function () {
					e.lineTo(t, n);
				});
			}),
			(this.arc = function (e, t, n, i, r, o, a) {
				w(function () {
					e.arc(t, n, i, r, o, a);
				});
			}),
			(this.curveTo = function (e, t, n, i, r, o, a) {
				w(function () {
					e.curveTo(t, n, i, r, o, a);
				});
			}),
			(this.close = function (e) {
				w(function () {
					e.close();
				});
			}),
			(this.rect = function (e, t, n, i, r) {
				w(function () {
					e.rect(t, n, i, r);
				});
			}),
			(this.clip = function (e) {
				w(function () {
					e.clip();
				});
			}),
			(this.strokeColor = function (e, t, n, i, r, o, a, s) {
				w(function () {
					e.strokeColor(t, n, i, r, o, a, s);
				});
			}),
			(this.fillColor = function (e, t, n, i, r) {
				w(function () {
					e.fillColor(t, n, i, r);
				});
			}),
			(this.strokeLayer = function (e, t, n, i, r) {
				w(function () {
					e.strokeLayer(t, n, i, r);
				});
			}),
			(this.fillLayer = function (e, t) {
				w(function () {
					e.fillLayer(t);
				});
			}),
			(this.push = function (e) {
				w(function () {
					e.push();
				});
			}),
			(this.pop = function (e) {
				w(function () {
					e.pop();
				});
			}),
			(this.reset = function (e) {
				w(function () {
					e.reset();
				});
			}),
			(this.setTransform = function (e, t, n, i, r, o, a) {
				w(function () {
					e.setTransform(t, n, i, r, o, a);
				});
			}),
			(this.transform = function (e, t, n, i, r, o, a) {
				w(function () {
					e.transform(t, n, i, r, o, a);
				});
			}),
			(this.setChannelMask = function (e, t) {
				w(function () {
					e.setChannelMask(t);
				});
			}),
			(this.setMiterLimit = function (e, t) {
				w(function () {
					e.setMiterLimit(t);
				});
			}),
			(this.dispose = function (e) {
				w(function () {
					e.dispose();
				});
			}),
			(this.distort = function (e, t, n, i, r, o, a) {
				w(function () {
					e.distort(t, n, i, r, o, a);
				});
			}),
			(this.move = function (e, t, n, i, r) {
				w(function () {
					e.move(t, n, i, r);
				});
			}),
			(this.shade = function (e, t) {
				w(function () {
					e.shade(t);
				});
			}),
			(this.scale = function (e) {
				(o.style.transform =
					o.style.WebkitTransform =
					o.style.MozTransform =
					o.style.OTransform =
					o.style.msTransform =
						"scale(" + e + "," + e + ")"),
					(r = e),
					(u.style.width = n * r + "px"),
					(u.style.height = i * r + "px");
			}),
			(this.getScale = function () {
				return r;
			}),
			(this.flatten = function () {
				var e = document.createElement("canvas");
				(e.width = a.width), (e.height = a.height);
				var t = e.getContext("2d");
				return (
					(function e(n, i, r) {
						if (n.width > 0 && n.height > 0) {
							var o = t.globalAlpha;
							(t.globalAlpha *= n.alpha / 255),
								t.drawImage(n.getCanvas(), i, r);
							for (
								var a = (function (e) {
										var t = [];
										for (var n in e.children) t.push(e.children[n]);
										return (
											t.sort(function (e, t) {
												var n = e.z - t.z;
												if (0 !== n) return n;
												var i = e.getElement(),
													r = t.getElement().compareDocumentPosition(i);
												return r & Node.DOCUMENT_POSITION_PRECEDING
													? -1
													: r & Node.DOCUMENT_POSITION_FOLLOWING
													? 1
													: 0;
											}),
											t
										);
									})(n),
									s = 0;
								s < a.length;
								s++
							) {
								var u = a[s];
								e(u, i + u.x, r + u.y);
							}
							t.globalAlpha = o;
						}
					})(a, 0, 0),
					e
				);
			});
	}),
	(e.Display.VisibleLayer = function (t, n) {
		e.Layer.apply(this, [t, n]);
		var i = this;
		(this.__unique_id = e.Display.VisibleLayer.__next_id++),
			(this.alpha = 255),
			(this.x = 0),
			(this.y = 0),
			(this.z = 0),
			(this.matrix = [1, 0, 0, 1, 0, 0]),
			(this.parent = null),
			(this.children = {});
		var r = i.getCanvas();
		(r.style.position = "absolute"),
			(r.style.left = "0px"),
			(r.style.top = "0px");
		var o = document.createElement("div");
		o.appendChild(r),
			(o.style.width = t + "px"),
			(o.style.height = n + "px"),
			(o.style.position = "absolute"),
			(o.style.left = "0px"),
			(o.style.top = "0px"),
			(o.style.overflow = "hidden");
		var a = this.resize;
		(this.resize = function (e, t) {
			(o.style.width = e + "px"), (o.style.height = t + "px"), a(e, t);
		}),
			(this.getElement = function () {
				return o;
			});
		var s = "translate(0px, 0px)",
			u = "matrix(1, 0, 0, 1, 0, 0)";
		(this.translate = function (e, t) {
			(i.x = e),
				(i.y = t),
				(s = "translate(" + e + "px," + t + "px)"),
				(o.style.transform =
					o.style.WebkitTransform =
					o.style.MozTransform =
					o.style.OTransform =
					o.style.msTransform =
						s + " " + u);
		}),
			(this.move = function (e, t, n, r) {
				i.parent !== e &&
					(i.parent && delete i.parent.children[i.__unique_id],
					(i.parent = e),
					(e.children[i.__unique_id] = i),
					e.getElement().appendChild(o));
				i.translate(t, n), (i.z = r), (o.style.zIndex = r);
			}),
			(this.shade = function (e) {
				(i.alpha = e), (o.style.opacity = e / 255);
			}),
			(this.dispose = function () {
				i.parent &&
					(delete i.parent.children[i.__unique_id], (i.parent = null)),
					o.parentNode && o.parentNode.removeChild(o);
			}),
			(this.distort = function (e, t, n, r, a, l) {
				(i.matrix = [e, t, n, r, a, l]),
					(u =
						"matrix(" +
						e +
						"," +
						t +
						"," +
						n +
						"," +
						r +
						"," +
						a +
						"," +
						l +
						")"),
					(o.style.transform =
						o.style.WebkitTransform =
						o.style.MozTransform =
						o.style.OTransform =
						o.style.msTransform =
							s + " " + u);
			});
	}),
	(e.Display.VisibleLayer.__next_id = 0),
	(e.Display.Statistics = function (e) {
		(e = e || {}),
			(this.processingLag = e.processingLag),
			(this.desktopFps = e.desktopFps),
			(this.serverFps = e.serverFps),
			(this.clientFps = e.clientFps),
			(this.dropRate = e.dropRate);
	}),
	((e = e || {}).Event = function (e) {
		(this.type = e),
			(this.timestamp = new Date().getTime()),
			(this.getAge = function () {
				return new Date().getTime() - this.timestamp;
			}),
			(this.invokeLegacyHandler = function (e) {});
	}),
	(e.Event.DOMEvent = function (t, n) {
		e.Event.call(this, t),
			(n = n || []),
			Array.isArray(n) || (n = [n]),
			(this.preventDefault = function () {
				n.forEach(function (e) {
					e.preventDefault && e.preventDefault(), (e.returnValue = !1);
				});
			}),
			(this.stopPropagation = function () {
				n.forEach(function (e) {
					e.stopPropagation();
				});
			});
	}),
	(e.Event.DOMEvent.cancelEvent = function (e) {
		e.stopPropagation(),
			e.preventDefault && e.preventDefault(),
			(e.returnValue = !1);
	}),
	(e.Event.Target = function () {
		var e = {};
		(this.on = function (t, n) {
			var i = e[t];
			i || (e[t] = i = []), i.push(n);
		}),
			(this.onEach = function (e, t) {
				e.forEach(function (e) {
					this.on(e, t);
				}, this);
			}),
			(this.dispatch = function (t) {
				t.invokeLegacyHandler(this);
				var n = e[t.type];
				if (n) for (var i = 0; i < n.length; i++) n[i](t, this);
			}),
			(this.off = function (t, n) {
				var i = e[t];
				if (!i) return !1;
				for (var r = 0; r < i.length; r++)
					if (i[r] === n) return i.splice(r, 1), !0;
				return !1;
			}),
			(this.offEach = function (e, t) {
				var n = !1;
				return (
					e.forEach(function (e) {
						n |= this.off(e, t);
					}, this),
					n
				);
			});
	}),
	((e = e || {}).InputSink = function () {
		var e = this,
			t = document.createElement("textarea");
		(t.style.position = "fixed"),
			(t.style.outline = "none"),
			(t.style.border = "none"),
			(t.style.margin = "0"),
			(t.style.padding = "0"),
			(t.style.height = "0"),
			(t.style.width = "0"),
			(t.style.left = "0"),
			(t.style.bottom = "0"),
			(t.style.resize = "none"),
			(t.style.background = "transparent"),
			(t.style.color = "transparent"),
			t.addEventListener(
				"keypress",
				function (e) {
					t.value = "";
				},
				!1
			),
			t.addEventListener(
				"compositionend",
				function (e) {
					e.data && (t.value = "");
				},
				!1
			),
			t.addEventListener(
				"input",
				function (e) {
					e.data && !e.isComposing && (t.value = "");
				},
				!1
			),
			t.addEventListener(
				"focus",
				function () {
					window.setTimeout(function () {
						t.click(), t.select();
					}, 0);
				},
				!0
			),
			(this.focus = function () {
				window.setTimeout(function () {
					t.focus();
				}, 0);
			}),
			(this.getElement = function () {
				return t;
			}),
			document.addEventListener(
				"keydown",
				function (t) {
					var n = document.activeElement;
					if (n && n !== document.body) {
						var i = n.getBoundingClientRect();
						if (i.left + i.width > 0 && i.top + i.height > 0) return;
					}
					e.focus();
				},
				!0
			);
	}),
	((e = e || {}).InputStream = function (e, t) {
		var n = this;
		(this.index = t),
			(this.onblob = null),
			(this.onend = null),
			(this.sendAck = function (t, i) {
				e.sendAck(n.index, t, i);
			});
	}),
	((e = e || {}).IntegerPool = function () {
		var e = this,
			t = [];
		(this.next_int = 0),
			(this.next = function () {
				return t.length > 0 ? t.shift() : e.next_int++;
			}),
			(this.free = function (e) {
				t.push(e);
			});
	}),
	((e = e || {}).JSONReader = function (t) {
		var n = this,
			i = new e.StringReader(t),
			r = "";
		(this.getLength = function () {
			return r.length;
		}),
			(this.getJSON = function () {
				return JSON.parse(r);
			}),
			(i.ontext = function (e) {
				(r += e), n.onprogress && n.onprogress(e.length);
			}),
			(i.onend = function () {
				n.onend && n.onend();
			}),
			(this.onprogress = null),
			(this.onend = null);
	}),
	((e = e || {}).Keyboard = function (t) {
		var n = this,
			i = "_GUAC_KEYBOARD_HANDLED_BY_" + e.Keyboard._nextID++;
		(this.onkeydown = null), (this.onkeyup = null);
		var r = {
			keyupUnreliable: !1,
			altIsTypableOnly: !1,
			capsLockKeyupUnreliable: !1,
		};
		navigator &&
			navigator.platform &&
			(navigator.platform.match(/ipad|iphone|ipod/i)
				? (r.keyupUnreliable = !0)
				: navigator.platform.match(/^mac/i) &&
				  ((r.altIsTypableOnly = !0), (r.capsLockKeyupUnreliable = !0)));
		var o = function (t) {
				var n = this;
				(this.keyCode = t ? t.which || t.keyCode : 0),
					(this.keyIdentifier = t && t.keyIdentifier),
					(this.key = t && t.key),
					(this.location = t ? L(t) : 0),
					(this.modifiers = t
						? e.Keyboard.ModifierState.fromKeyboardEvent(t)
						: new e.Keyboard.ModifierState()),
					(this.timestamp = new Date().getTime()),
					(this.defaultPrevented = !1),
					(this.keysym = null),
					(this.reliable = !1),
					(this.getAge = function () {
						return new Date().getTime() - n.timestamp;
					});
			},
			a = function (e) {
				o.call(this, e),
					(this.keysym =
						S(this.key, this.location) || E(this.keyCode, this.location)),
					(this.keyupReliable = !r.keyupUnreliable),
					this.keysym && !w(this.keysym) && (this.reliable = !0),
					!this.keysym &&
						I(this.keyCode, this.keyIdentifier) &&
						(this.keysym = S(
							this.keyIdentifier,
							this.location,
							this.modifiers.shift
						)),
					((this.modifiers.meta &&
						65511 !== this.keysym &&
						65512 !== this.keysym) ||
						(65509 === this.keysym && r.capsLockKeyupUnreliable)) &&
						(this.keyupReliable = !1);
				var t = !this.modifiers.ctrl && !r.altIsTypableOnly;
				((!this.modifiers.alt && this.modifiers.ctrl) ||
					(t && this.modifiers.alt) ||
					this.modifiers.meta ||
					this.modifiers.hyper) &&
					(this.reliable = !0),
					(v[this.keyCode] = this.keysym);
			};
		a.prototype = new o();
		var s = function (e) {
			o.call(this, e), (this.keysym = T(this.keyCode)), (this.reliable = !0);
		};
		s.prototype = new o();
		var u = function (e) {
			o.call(this, e),
				(this.keysym =
					E(this.keyCode, this.location) || S(this.key, this.location)),
				n.pressed[this.keysym] ||
					(this.keysym = v[this.keyCode] || this.keysym),
				(this.reliable = !0);
		};
		u.prototype = new o();
		var l = [],
			c = {
				8: [65288],
				9: [65289],
				12: [65291, 65291, 65291, 65461],
				13: [65293],
				16: [65505, 65505, 65506],
				17: [65507, 65507, 65508],
				18: [65513, 65513, 65027],
				19: [65299],
				20: [65509],
				27: [65307],
				32: [32],
				33: [65365, 65365, 65365, 65465],
				34: [65366, 65366, 65366, 65459],
				35: [65367, 65367, 65367, 65457],
				36: [65360, 65360, 65360, 65463],
				37: [65361, 65361, 65361, 65460],
				38: [65362, 65362, 65362, 65464],
				39: [65363, 65363, 65363, 65462],
				40: [65364, 65364, 65364, 65458],
				45: [65379, 65379, 65379, 65456],
				46: [65535, 65535, 65535, 65454],
				91: [65511],
				92: [65512],
				93: [65383],
				96: [65456],
				97: [65457],
				98: [65458],
				99: [65459],
				100: [65460],
				101: [65461],
				102: [65462],
				103: [65463],
				104: [65464],
				105: [65465],
				106: [65450],
				107: [65451],
				109: [65453],
				110: [65454],
				111: [65455],
				112: [65470],
				113: [65471],
				114: [65472],
				115: [65473],
				116: [65474],
				117: [65475],
				118: [65476],
				119: [65477],
				120: [65478],
				121: [65479],
				122: [65480],
				123: [65481],
				144: [65407],
				145: [65300],
				225: [65027],
			},
			h = {
				Again: [65382],
				AllCandidates: [65341],
				Alphanumeric: [65328],
				Alt: [65513, 65513, 65027],
				Attn: [64782],
				AltGraph: [65027],
				ArrowDown: [65364],
				ArrowLeft: [65361],
				ArrowRight: [65363],
				ArrowUp: [65362],
				Backspace: [65288],
				CapsLock: [65509],
				Cancel: [65385],
				Clear: [65291],
				Convert: [65313],
				Copy: [64789],
				Crsel: [64796],
				CrSel: [64796],
				CodeInput: [65335],
				Compose: [65312],
				Control: [65507, 65507, 65508],
				ContextMenu: [65383],
				Delete: [65535],
				Down: [65364],
				End: [65367],
				Enter: [65293],
				EraseEof: [64774],
				Escape: [65307],
				Execute: [65378],
				Exsel: [64797],
				ExSel: [64797],
				F1: [65470],
				F2: [65471],
				F3: [65472],
				F4: [65473],
				F5: [65474],
				F6: [65475],
				F7: [65476],
				F8: [65477],
				F9: [65478],
				F10: [65479],
				F11: [65480],
				F12: [65481],
				F13: [65482],
				F14: [65483],
				F15: [65484],
				F16: [65485],
				F17: [65486],
				F18: [65487],
				F19: [65488],
				F20: [65489],
				F21: [65490],
				F22: [65491],
				F23: [65492],
				F24: [65493],
				Find: [65384],
				GroupFirst: [65036],
				GroupLast: [65038],
				GroupNext: [65032],
				GroupPrevious: [65034],
				FullWidth: null,
				HalfWidth: null,
				HangulMode: [65329],
				Hankaku: [65321],
				HanjaMode: [65332],
				Help: [65386],
				Hiragana: [65317],
				HiraganaKatakana: [65319],
				Home: [65360],
				Hyper: [65517, 65517, 65518],
				Insert: [65379],
				JapaneseHiragana: [65317],
				JapaneseKatakana: [65318],
				JapaneseRomaji: [65316],
				JunjaMode: [65336],
				KanaMode: [65325],
				KanjiMode: [65313],
				Katakana: [65318],
				Left: [65361],
				Meta: [65511, 65511, 65512],
				ModeChange: [65406],
				NumLock: [65407],
				PageDown: [65366],
				PageUp: [65365],
				Pause: [65299],
				Play: [64790],
				PreviousCandidate: [65342],
				PrintScreen: [65377],
				Redo: [65382],
				Right: [65363],
				RomanCharacters: null,
				Scroll: [65300],
				Select: [65376],
				Separator: [65452],
				Shift: [65505, 65505, 65506],
				SingleCandidate: [65340],
				Super: [65515, 65515, 65516],
				Tab: [65289],
				UIKeyInputDownArrow: [65364],
				UIKeyInputEscape: [65307],
				UIKeyInputLeftArrow: [65361],
				UIKeyInputRightArrow: [65363],
				UIKeyInputUpArrow: [65362],
				Up: [65362],
				Undo: [65381],
				Win: [65511, 65511, 65512],
				Zenkaku: [65320],
				ZenkakuHankaku: [65322],
			},
			d = {
				65027: !0,
				65505: !0,
				65506: !0,
				65507: !0,
				65508: !0,
				65509: !0,
				65511: !0,
				65512: !0,
				65513: !0,
				65514: !0,
				65515: !0,
				65516: !0,
			};
		(this.modifiers = new e.Keyboard.ModifierState()), (this.pressed = {});
		var f = {},
			p = {},
			v = {},
			g = null,
			m = null,
			y = function (e, t) {
				return e ? e[t] || e[0] : null;
			},
			w = function (e) {
				return (e >= 0 && e <= 255) || 16777216 == (4294901760 & e);
			};
		function S(e, t, n) {
			if (!e) return null;
			var i,
				r = e.indexOf("U+");
			if (r >= 0) {
				var o = e.substring(r + 2);
				i = String.fromCharCode(parseInt(o, 16));
			} else {
				if (1 !== e.length || 3 === t) return y(h[e], t);
				i = e;
			}
			return (
				!0 === n ? (i = i.toUpperCase()) : !1 === n && (i = i.toLowerCase()),
				T(i.charCodeAt(0))
			);
		}
		function T(e) {
			return (function (e) {
				return e <= 31 || (e >= 127 && e <= 159);
			})(e)
				? 65280 | e
				: e >= 0 && e <= 255
				? e
				: e >= 256 && e <= 1114111
				? 16777216 | e
				: null;
		}
		function E(e, t) {
			return y(c[e], t);
		}
		var I = function (e, t) {
			if (!t) return !1;
			var n = t.indexOf("U+");
			return (
				-1 === n ||
				e !== parseInt(t.substring(n + 2), 16) ||
				(e >= 65 && e <= 90) ||
				(e >= 48 && e <= 57)
			);
		};
		(this.press = function (e) {
			if (null !== e) {
				if (!n.pressed[e] && ((n.pressed[e] = !0), n.onkeydown)) {
					var t = n.onkeydown(e);
					return (
						(p[e] = t),
						window.clearTimeout(g),
						window.clearInterval(m),
						d[e] ||
							(g = window.setTimeout(function () {
								m = window.setInterval(function () {
									n.onkeyup(e), n.onkeydown(e);
								}, 50);
							}, 500)),
						t
					);
				}
				return p[e] || !1;
			}
		}),
			(this.release = function (e) {
				n.pressed[e] &&
					(delete n.pressed[e],
					delete f[e],
					window.clearTimeout(g),
					window.clearInterval(m),
					null !== e && n.onkeyup && n.onkeyup(e));
			}),
			(this.type = function (e) {
				for (var t = 0; t < e.length; t++) {
					var i = T(e.codePointAt ? e.codePointAt(t) : e.charCodeAt(t));
					n.press(i), n.release(i);
				}
			}),
			(this.reset = function () {
				for (var e in n.pressed) n.release(parseInt(e));
				l = [];
			});
		var b = function (e, t, i) {
				var r,
					o = i.modifiers[e],
					a = n.modifiers[e];
				if (-1 === t.indexOf(i.keysym))
					if (a && !1 === o) for (r = 0; r < t.length; r++) n.release(t[r]);
					else if (!a && o) {
						for (r = 0; r < t.length; r++) if (n.pressed[t[r]]) return;
						var s = t[0];
						i.keysym && (f[s] = !0), n.press(s);
					}
			},
			C = function (e) {
				b("alt", [65513, 65514, 65027], e),
					b("shift", [65505, 65506], e),
					b("ctrl", [65507, 65508], e),
					b("meta", [65511, 65512], e),
					b("hyper", [65515, 65516], e),
					(n.modifiers = e.modifiers);
			};
		function k() {
			var e,
				t = A();
			if (!t) return !1;
			do {
				(e = t), (t = A());
			} while (null !== t);
			return (
				(function () {
					for (var e in n.pressed) if (!f[e]) return !1;
					return !0;
				})() && n.reset(),
				e.defaultPrevented
			);
		}
		var A = function () {
				var e = l[0];
				if (!e) return null;
				if (!(e instanceof a))
					return e instanceof u && !r.keyupUnreliable
						? (t = e.keysym)
							? (n.release(t),
							  delete v[e.keyCode],
							  (e.defaultPrevented = !0),
							  C(e),
							  l.shift())
							: (n.reset(), e)
						: l.shift();
				var t = null,
					i = [];
				if (65511 === e.keysym || 65512 === e.keysym) {
					if (1 === l.length) return null;
					if (l[1].keysym !== e.keysym) {
						if (!l[1].modifiers.meta) return l.shift();
					} else if (l[1] instanceof a) return l.shift();
				}
				if (
					(e.reliable
						? ((t = e.keysym), (i = l.splice(0, 1)))
						: l[1] instanceof s
						? ((t = l[1].keysym), (i = l.splice(0, 2)))
						: l[1] && ((t = e.keysym), (i = l.splice(0, 1))),
					i.length > 0)
				) {
					if ((C(e), t)) {
						!(function (e) {
							n.modifiers.ctrl &&
								n.modifiers.alt &&
								((e >= 65 && e <= 90) ||
									(e >= 97 && e <= 122) ||
									((e <= 255 || 16777216 == (4278190080 & e)) &&
										(n.release(65507),
										n.release(65508),
										n.release(65513),
										n.release(65514))));
						})(t);
						var o = !n.press(t);
						(v[e.keyCode] = t), e.keyupReliable || n.release(t);
						for (var c = 0; c < i.length; c++) i[c].defaultPrevented = o;
					}
					return e;
				}
				return null;
			},
			L = function (e) {
				return "location" in e
					? e.location
					: "keyLocation" in e
					? e.keyLocation
					: 0;
			},
			M = function (e) {
				return !e[i] && ((e[i] = !0), !0);
			};
		(this.listenTo = function (e) {
			e.addEventListener(
				"keydown",
				function (e) {
					if (n.onkeydown && M(e)) {
						var t = new a(e);
						229 !== t.keyCode && (l.push(t), k() && e.preventDefault());
					}
				},
				!0
			),
				e.addEventListener(
					"keypress",
					function (e) {
						(n.onkeydown || n.onkeyup) &&
							M(e) &&
							(l.push(new s(e)), k() && e.preventDefault());
					},
					!0
				),
				e.addEventListener(
					"keyup",
					function (e) {
						n.onkeyup && M(e) && (e.preventDefault(), l.push(new u(e)), k());
					},
					!0
				);
			var t = function (t) {
					(n.onkeydown || n.onkeyup) &&
						M(t) &&
						t.data &&
						!t.isComposing &&
						(e.removeEventListener("compositionend", i, !1), n.type(t.data));
				},
				i = function (i) {
					(n.onkeydown || n.onkeyup) &&
						M(i) &&
						i.data &&
						(e.removeEventListener("input", t, !1), n.type(i.data));
				};
			e.addEventListener("input", t, !1),
				e.addEventListener("compositionend", i, !1);
		}),
			t && n.listenTo(t);
	}),
	(e.Keyboard._nextID = 0),
	(e.Keyboard.ModifierState = function () {
		(this.shift = !1),
			(this.ctrl = !1),
			(this.alt = !1),
			(this.meta = !1),
			(this.hyper = !1);
	}),
	(e.Keyboard.ModifierState.fromKeyboardEvent = function (t) {
		var n = new e.Keyboard.ModifierState();
		return (
			(n.shift = t.shiftKey),
			(n.ctrl = t.ctrlKey),
			(n.alt = t.altKey),
			(n.meta = t.metaKey),
			t.getModifierState &&
				(n.hyper =
					t.getModifierState("OS") ||
					t.getModifierState("Super") ||
					t.getModifierState("Hyper") ||
					t.getModifierState("Win")),
			n
		);
	}),
	((e = e || {}).Layer = function (t, n) {
		var i = this,
			r = document.createElement("canvas"),
			o = r.getContext("2d");
		o.save();
		var a = !0,
			s = !0,
			u = 0,
			l = {
				1: "destination-in",
				2: "destination-out",
				4: "source-in",
				6: "source-atop",
				8: "source-out",
				9: "destination-atop",
				10: "xor",
				11: "destination-over",
				12: "copy",
				14: "source-over",
				15: "lighter",
			},
			c = function (e, t) {
				(e = e || 0), (t = t || 0);
				var n = 64 * Math.ceil(e / 64),
					s = 64 * Math.ceil(t / 64);
				if (r.width !== n || r.height !== s) {
					var l = null;
					if (!a && 0 !== r.width && 0 !== r.height)
						((l = document.createElement("canvas")).width = Math.min(
							i.width,
							e
						)),
							(l.height = Math.min(i.height, t)),
							l
								.getContext("2d")
								.drawImage(r, 0, 0, l.width, l.height, 0, 0, l.width, l.height);
					var c = o.globalCompositeOperation;
					(r.width = n),
						(r.height = s),
						l &&
							o.drawImage(l, 0, 0, l.width, l.height, 0, 0, l.width, l.height),
						(o.globalCompositeOperation = c),
						(u = 0),
						o.save();
				} else i.reset();
				(i.width = e), (i.height = t);
			};
		function h(e, t, n, r) {
			var o,
				a,
				s = n + e,
				u = r + t;
			(o = s > i.width ? s : i.width),
				(a = u > i.height ? u : i.height),
				i.resize(o, a);
		}
		(this.autosize = !1),
			(this.width = t),
			(this.height = n),
			(this.getCanvas = function () {
				return r;
			}),
			(this.toCanvas = function () {
				var e = document.createElement("canvas");
				return (
					(e.width = i.width),
					(e.height = i.height),
					e.getContext("2d").drawImage(i.getCanvas(), 0, 0),
					e
				);
			}),
			(this.resize = function (e, t) {
				(e === i.width && t === i.height) || c(e, t);
			}),
			(this.drawImage = function (e, t, n) {
				i.autosize && h(e, t, n.width, n.height),
					o.drawImage(n, e, t),
					(a = !1);
			}),
			(this.transfer = function (t, n, r, s, u, l, c, d) {
				var f = t.getCanvas();
				if (
					!(n >= f.width || r >= f.height) &&
					(n + s > f.width && (s = f.width - n),
					r + u > f.height && (u = f.height - r),
					0 !== s && 0 !== u)
				) {
					i.autosize && h(l, c, s, u);
					for (
						var p = t.getCanvas().getContext("2d").getImageData(n, r, s, u),
							v = o.getImageData(l, c, s, u),
							g = 0;
						g < s * u * 4;
						g += 4
					) {
						var m = new e.Layer.Pixel(
								p.data[g],
								p.data[g + 1],
								p.data[g + 2],
								p.data[g + 3]
							),
							y = new e.Layer.Pixel(
								v.data[g],
								v.data[g + 1],
								v.data[g + 2],
								v.data[g + 3]
							);
						d(m, y),
							(v.data[g] = y.red),
							(v.data[g + 1] = y.green),
							(v.data[g + 2] = y.blue),
							(v.data[g + 3] = y.alpha);
					}
					o.putImageData(v, l, c), (a = !1);
				}
			}),
			(this.put = function (e, t, n, r, s, u, l) {
				var c = e.getCanvas();
				if (
					!(t >= c.width || n >= c.height) &&
					(t + r > c.width && (r = c.width - t),
					n + s > c.height && (s = c.height - n),
					0 !== r && 0 !== s)
				) {
					i.autosize && h(u, l, r, s);
					var d = e.getCanvas().getContext("2d").getImageData(t, n, r, s);
					o.putImageData(d, u, l), (a = !1);
				}
			}),
			(this.copy = function (e, t, n, r, s, u, l) {
				var c = e.getCanvas();
				t >= c.width ||
					n >= c.height ||
					(t + r > c.width && (r = c.width - t),
					n + s > c.height && (s = c.height - n),
					0 !== r &&
						0 !== s &&
						(i.autosize && h(u, l, r, s),
						o.drawImage(c, t, n, r, s, u, l, r, s),
						(a = !1)));
			}),
			(this.moveTo = function (e, t) {
				s && (o.beginPath(), (s = !1)),
					i.autosize && h(e, t, 0, 0),
					o.moveTo(e, t);
			}),
			(this.lineTo = function (e, t) {
				s && (o.beginPath(), (s = !1)),
					i.autosize && h(e, t, 0, 0),
					o.lineTo(e, t);
			}),
			(this.arc = function (e, t, n, r, a, u) {
				s && (o.beginPath(), (s = !1)),
					i.autosize && h(e, t, 0, 0),
					o.arc(e, t, n, r, a, u);
			}),
			(this.curveTo = function (e, t, n, r, a, u) {
				s && (o.beginPath(), (s = !1)),
					i.autosize && h(a, u, 0, 0),
					o.bezierCurveTo(e, t, n, r, a, u);
			}),
			(this.close = function () {
				o.closePath(), (s = !0);
			}),
			(this.rect = function (e, t, n, r) {
				s && (o.beginPath(), (s = !1)),
					i.autosize && h(e, t, n, r),
					o.rect(e, t, n, r);
			}),
			(this.clip = function () {
				o.clip(), (s = !0);
			}),
			(this.strokeColor = function (e, t, n, i, r, u, l) {
				(o.lineCap = e),
					(o.lineJoin = t),
					(o.lineWidth = n),
					(o.strokeStyle =
						"rgba(" + i + "," + r + "," + u + "," + l / 255 + ")"),
					o.stroke(),
					(a = !1),
					(s = !0);
			}),
			(this.fillColor = function (e, t, n, i) {
				(o.fillStyle = "rgba(" + e + "," + t + "," + n + "," + i / 255 + ")"),
					o.fill(),
					(a = !1),
					(s = !0);
			}),
			(this.strokeLayer = function (e, t, n, i) {
				(o.lineCap = e),
					(o.lineJoin = t),
					(o.lineWidth = n),
					(o.strokeStyle = o.createPattern(i.getCanvas(), "repeat")),
					o.stroke(),
					(a = !1),
					(s = !0);
			}),
			(this.fillLayer = function (e) {
				(o.fillStyle = o.createPattern(e.getCanvas(), "repeat")),
					o.fill(),
					(a = !1),
					(s = !0);
			}),
			(this.push = function () {
				o.save(), u++;
			}),
			(this.pop = function () {
				u > 0 && (o.restore(), u--);
			}),
			(this.reset = function () {
				for (; u > 0; ) o.restore(), u--;
				o.restore(), o.save(), o.beginPath(), (s = !1);
			}),
			(this.setTransform = function (e, t, n, i, r, a) {
				o.setTransform(e, t, n, i, r, a);
			}),
			(this.transform = function (e, t, n, i, r, a) {
				o.transform(e, t, n, i, r, a);
			}),
			(this.setChannelMask = function (e) {
				o.globalCompositeOperation = l[e];
			}),
			(this.setMiterLimit = function (e) {
				o.miterLimit = e;
			}),
			c(t, n),
			(r.style.zIndex = -1);
	}),
	(e.Layer.ROUT = 2),
	(e.Layer.ATOP = 6),
	(e.Layer.XOR = 10),
	(e.Layer.ROVER = 11),
	(e.Layer.OVER = 14),
	(e.Layer.PLUS = 15),
	(e.Layer.RIN = 1),
	(e.Layer.IN = 4),
	(e.Layer.OUT = 8),
	(e.Layer.RATOP = 9),
	(e.Layer.SRC = 12),
	(e.Layer.Pixel = function (e, t, n, i) {
		(this.red = e), (this.green = t), (this.blue = n), (this.alpha = i);
	}),
	((e = e || {}).Mouse = function (t) {
		e.Mouse.Event.Target.call(this);
		var n = this;
		(this.touchMouseThreshold = 3),
			(this.scrollThreshold = 53),
			(this.PIXELS_PER_LINE = 18),
			(this.PIXELS_PER_PAGE = 16 * this.PIXELS_PER_LINE);
		var i = [
				e.Mouse.State.Buttons.LEFT,
				e.Mouse.State.Buttons.MIDDLE,
				e.Mouse.State.Buttons.RIGHT,
			],
			r = 0,
			o = 0;
		function a() {
			r = n.touchMouseThreshold;
		}
		function s(t) {
			var i = t.deltaY || -t.wheelDeltaY || -t.wheelDelta;
			if (
				(i
					? 1 === t.deltaMode
						? (i = t.deltaY * n.PIXELS_PER_LINE)
						: 2 === t.deltaMode && (i = t.deltaY * n.PIXELS_PER_PAGE)
					: (i = t.detail * n.PIXELS_PER_LINE),
				(o += i) <= -n.scrollThreshold)
			) {
				do {
					n.click(e.Mouse.State.Buttons.UP), (o += n.scrollThreshold);
				} while (o <= -n.scrollThreshold);
				o = 0;
			}
			if (o >= n.scrollThreshold) {
				do {
					n.click(e.Mouse.State.Buttons.DOWN), (o -= n.scrollThreshold);
				} while (o >= n.scrollThreshold);
				o = 0;
			}
			e.Event.DOMEvent.cancelEvent(t);
		}
		t.addEventListener(
			"contextmenu",
			function (t) {
				e.Event.DOMEvent.cancelEvent(t);
			},
			!1
		),
			t.addEventListener(
				"mousemove",
				function (i) {
					if (r) return e.Event.DOMEvent.cancelEvent(i), void r--;
					n.move(e.Position.fromClientPosition(t, i.clientX, i.clientY), i);
				},
				!1
			),
			t.addEventListener(
				"mousedown",
				function (t) {
					if (r) e.Event.DOMEvent.cancelEvent(t);
					else {
						var o = i[t.button];
						o && n.press(o, t);
					}
				},
				!1
			),
			t.addEventListener(
				"mouseup",
				function (t) {
					if (r) e.Event.DOMEvent.cancelEvent(t);
					else {
						var o = i[t.button];
						o && n.release(o, t);
					}
				},
				!1
			),
			t.addEventListener(
				"mouseout",
				function (e) {
					e || (e = window.event);
					for (var i = e.relatedTarget || e.toElement; i; ) {
						if (i === t) return;
						i = i.parentNode;
					}
					n.reset(e), n.out(e);
				},
				!1
			),
			t.addEventListener(
				"selectstart",
				function (t) {
					e.Event.DOMEvent.cancelEvent(t);
				},
				!1
			),
			t.addEventListener("touchmove", a, !1),
			t.addEventListener("touchstart", a, !1),
			t.addEventListener("touchend", a, !1),
			t.addEventListener("DOMMouseScroll", s, !1),
			t.addEventListener("mousewheel", s, !1),
			t.addEventListener("wheel", s, !1);
		var u = (function () {
			var e = document.createElement("div");
			if (!("cursor" in e.style)) return !1;
			try {
				e.style.cursor =
					"url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEX///+nxBvIAAAACklEQVQI12NgAAAAAgAB4iG8MwAAAABJRU5ErkJggg==) 0 0, auto";
			} catch (e) {
				return !1;
			}
			return /\burl\([^()]*\)\s+0\s+0\b/.test(e.style.cursor || "");
		})();
		this.setCursor = function (e, n, i) {
			if (u) {
				var r = e.toDataURL("image/png");
				return (
					(t.style.cursor = "url(" + r + ") " + n + " " + i + ", auto"), !0
				);
			}
			return !1;
		};
	}),
	(e.Mouse.State = function (t) {
		(t =
			arguments.length > 1
				? function (e, t, n, i, r, o, a) {
						return { x: e, y: t, left: n, middle: i, right: r, up: o, down: a };
				  }.apply(this, arguments)
				: t || {}),
			e.Position.call(this, t),
			(this.left = t.left || !1),
			(this.middle = t.middle || !1),
			(this.right = t.right || !1),
			(this.up = t.up || !1),
			(this.down = t.down || !1);
	}),
	(e.Mouse.State.Buttons = {
		LEFT: "left",
		MIDDLE: "middle",
		RIGHT: "right",
		UP: "up",
		DOWN: "down",
	}),
	(e.Mouse.Event = function (t, n, i) {
		e.Event.DOMEvent.call(this, t, i);
		var r = "on" + this.type;
		(this.state = n),
			(this.invokeLegacyHandler = function (e) {
				e[r] &&
					(this.preventDefault(), this.stopPropagation(), e[r](this.state));
			});
	}),
	(e.Mouse.Event.Target = function () {
		e.Event.Target.call(this),
			(this.currentState = new e.Mouse.State()),
			(this.press = function (t, n) {
				this.currentState[t] ||
					((this.currentState[t] = !0),
					this.dispatch(new e.Mouse.Event("mousedown", this.currentState, n)));
			}),
			(this.release = function (t, n) {
				this.currentState[t] &&
					((this.currentState[t] = !1),
					this.dispatch(new e.Mouse.Event("mouseup", this.currentState, n)));
			}),
			(this.click = function (e, t) {
				this.press(e, t), this.release(e, t);
			}),
			(this.move = function (t, n) {
				(this.currentState.x === t.x && this.currentState.y === t.y) ||
					((this.currentState.x = t.x),
					(this.currentState.y = t.y),
					this.dispatch(new e.Mouse.Event("mousemove", this.currentState, n)));
			}),
			(this.out = function (t) {
				this.dispatch(new e.Mouse.Event("mouseout", this.currentState, t));
			}),
			(this.reset = function (t) {
				for (var n in e.Mouse.State.Buttons)
					this.release(e.Mouse.State.Buttons[n], t);
			});
	}),
	(e.Mouse.Touchpad = function (t) {
		e.Mouse.Event.Target.call(this);
		var n = this;
		(this.scrollThreshold = 20 * (window.devicePixelRatio || 1)),
			(this.clickTimingThreshold = 250),
			(this.clickMoveThreshold = 10 * (window.devicePixelRatio || 1)),
			(this.currentState = new e.Mouse.State());
		var i = 0,
			r = 0,
			o = 0,
			a = 0,
			s = 0,
			u = { 1: "left", 2: "right", 3: "middle" },
			l = !1,
			c = null;
		t.addEventListener(
			"touchend",
			function (e) {
				if ((e.preventDefault(), l && 0 === e.touches.length)) {
					var t = new Date().getTime(),
						r = u[i];
					n.currentState[r] &&
						(n.release(r, e), c && (window.clearTimeout(c), (c = null))),
						t - a <= n.clickTimingThreshold &&
							s < n.clickMoveThreshold &&
							(n.press(r, e),
							(c = window.setTimeout(function () {
								n.release(r, e), (l = !1);
							}, n.clickTimingThreshold))),
						c || (l = !1);
				}
			},
			!1
		),
			t.addEventListener(
				"touchstart",
				function (e) {
					if (
						(e.preventDefault(),
						(i = Math.min(e.touches.length, 3)),
						c && (window.clearTimeout(c), (c = null)),
						!l)
					) {
						l = !0;
						var t = e.touches[0];
						(r = t.clientX),
							(o = t.clientY),
							(a = new Date().getTime()),
							(s = 0);
					}
				},
				!1
			),
			t.addEventListener(
				"touchmove",
				function (u) {
					u.preventDefault();
					var l = u.touches[0],
						c = l.clientX - r,
						h = l.clientY - o;
					if (((s += Math.abs(c) + Math.abs(h)), 1 === i)) {
						var d = 1 + s / (new Date().getTime() - a),
							f = new e.Position(n.currentState);
						(f.x += c * d),
							(f.y += h * d),
							(f.x = Math.min(Math.max(0, f.x), t.offsetWidth - 1)),
							(f.y = Math.min(Math.max(0, f.y), t.offsetHeight - 1)),
							n.move(f, u),
							(r = l.clientX),
							(o = l.clientY);
					} else if (2 === i) {
						var p;
						if (Math.abs(h) >= n.scrollThreshold)
							(p = h > 0 ? "down" : "up"),
								n.click(p, u),
								(r = l.clientX),
								(o = l.clientY);
					}
				},
				!1
			);
	}),
	(e.Mouse.Touchscreen = function (t) {
		e.Mouse.Event.Target.call(this);
		var n = this,
			i = !1,
			r = null,
			o = null,
			a = null,
			s = null;
		function u(e) {
			var t = e.touches[0] || e.changedTouches[0],
				i = t.clientX - r,
				a = t.clientY - o;
			return Math.sqrt(i * i + a * a) >= n.clickMoveThreshold;
		}
		function l() {
			window.clearTimeout(a), window.clearTimeout(s), (i = !1);
		}
		(this.scrollThreshold = 20 * (window.devicePixelRatio || 1)),
			(this.clickTimingThreshold = 250),
			(this.clickMoveThreshold = 16 * (window.devicePixelRatio || 1)),
			(this.longPressThreshold = 500),
			t.addEventListener(
				"touchend",
				function (r) {
					if (i)
						if (0 === r.touches.length && 1 === r.changedTouches.length) {
							if (
								(window.clearTimeout(s),
								n.release(e.Mouse.State.Buttons.LEFT, r),
								!u(r) && (r.preventDefault(), !n.currentState.left))
							) {
								var o = r.changedTouches[0];
								n.move(e.Position.fromClientPosition(t, o.clientX, o.clientY)),
									n.press(e.Mouse.State.Buttons.LEFT, r),
									(a = window.setTimeout(function () {
										n.release(e.Mouse.State.Buttons.LEFT, r), l();
									}, n.clickTimingThreshold));
							}
						} else l();
				},
				!1
			),
			t.addEventListener(
				"touchstart",
				function (u) {
					1 === u.touches.length
						? (u.preventDefault(),
						  (function (e) {
								var t = e.touches[0];
								(i = !0), (r = t.clientX), (o = t.clientY);
						  })(u),
						  window.clearTimeout(a),
						  (s = window.setTimeout(function () {
								var i = u.touches[0];
								n.move(e.Position.fromClientPosition(t, i.clientX, i.clientY)),
									n.click(e.Mouse.State.Buttons.RIGHT, u),
									l();
						  }, n.longPressThreshold)))
						: l();
				},
				!1
			),
			t.addEventListener(
				"touchmove",
				function (r) {
					if (i)
						if ((u(r) && window.clearTimeout(s), 1 === r.touches.length)) {
							if (n.currentState.left) {
								r.preventDefault();
								var o = r.touches[0];
								n.move(
									e.Position.fromClientPosition(t, o.clientX, o.clientY),
									r
								);
							}
						} else l();
				},
				!1
			);
	}),
	((e = (e = e || {}) || {}).Object = function (e, t) {
		var n = this,
			i = {};
		(this.index = t),
			(this.onbody = function (e, t, n) {
				var r = (function (e) {
					var t = i[e];
					if (!t) return null;
					var n = t.shift();
					return 0 === t.length && delete i[e], n;
				})(n);
				r && r(e, t);
			}),
			(this.onundefine = null),
			(this.requestInputStream = function (t, r) {
				r &&
					(function (e, t) {
						var n = i[e];
						n || ((n = []), (i[e] = n)), n.push(t);
					})(t, r),
					e.requestObjectInputStream(n.index, t);
			}),
			(this.createOutputStream = function (t, i) {
				return e.createObjectOutputStream(n.index, t, i);
			});
	}),
	(e.Object.ROOT_STREAM = "/"),
	(e.Object.STREAM_INDEX_MIMETYPE =
		"application/vnd.glyptodon.guacamole.stream-index+json"),
	((e = e || {}).OnScreenKeyboard = function (t) {
		var n = this,
			i = {},
			r = {},
			o = [],
			a = function (e, t) {
				e.classList ? e.classList.add(t) : (e.className += " " + t);
			},
			s = function (e, t) {
				e.classList
					? e.classList.remove(t)
					: (e.className = e.className.replace(/([^ ]+)[ ]*/g, function (e, n) {
							return n === t ? "" : e;
					  }));
			},
			u = 0,
			l = function (e, t, n, i) {
				(this.width = t),
					(this.height = n),
					(this.scale = function (r) {
						(e.style.width = t * r + "px"),
							(e.style.height = n * r + "px"),
							i &&
								((e.style.lineHeight = n * r + "px"),
								(e.style.fontSize = r + "px"));
					});
			},
			c = function (e) {
				for (var t = 0; t < e.length; t++) {
					if (!(e[t] in i)) return !1;
				}
				return !0;
			},
			h = function (e) {
				var t = n.keys[e];
				if (!t) return null;
				for (var i = t.length - 1; i >= 0; i--) {
					var r = t[i];
					if (c(r.requires)) return r;
				}
				return null;
			},
			d = function (e, t) {
				if (!r[e]) {
					a(t, "guac-keyboard-pressed");
					var o = h(e);
					if (o.modifier) {
						var u = "guac-keyboard-modifier-" + g(o.modifier),
							l = i[o.modifier];
						void 0 === l
							? (a(p, u),
							  (i[o.modifier] = o.keysym),
							  o.keysym && n.onkeydown && n.onkeydown(o.keysym))
							: (s(p, u), delete i[o.modifier], l && n.onkeyup && n.onkeyup(l));
					} else n.onkeydown && n.onkeydown(o.keysym);
					r[e] = !0;
				}
			},
			f = function (e, t) {
				if (r[e]) {
					s(t, "guac-keyboard-pressed");
					var i = h(e);
					!i.modifier && n.onkeyup && n.onkeyup(i.keysym), (r[e] = !1);
				}
			},
			p = document.createElement("div");
		(p.className = "guac-keyboard"),
			(p.onselectstart =
				p.onmousemove =
				p.onmouseup =
				p.onmousedown =
					function (e) {
						return u && u--, e.stopPropagation(), !1;
					}),
			(this.touchMouseThreshold = 3),
			(this.onkeydown = null),
			(this.onkeyup = null),
			(this.layout = new e.OnScreenKeyboard.Layout(t)),
			(this.getElement = function () {
				return p;
			}),
			(this.resize = function (e) {
				for (
					var t = Math.floor((10 * e) / n.layout.width) / 10, i = 0;
					i < o.length;
					i++
				) {
					o[i].scale(t);
				}
			});
		var v = function (t, n) {
			if (n instanceof Array) {
				for (var i = [], r = 0; r < n.length; r++)
					i.push(new e.OnScreenKeyboard.Key(n[r], t));
				return i;
			}
			return "number" == typeof n
				? [new e.OnScreenKeyboard.Key({ name: t, keysym: n })]
				: "string" == typeof n
				? [new e.OnScreenKeyboard.Key({ name: t, title: n })]
				: [new e.OnScreenKeyboard.Key(n, t)];
		};
		this.keys = (function (e) {
			var n = {};
			for (var i in t.keys) n[i] = v(i, e[i]);
			return n;
		})(t.keys);
		var g = function (e) {
			return e
				.replace(/([a-z])([A-Z])/g, "$1-$2")
				.replace(/[^A-Za-z0-9]+/g, "-")
				.toLowerCase();
		};
		!(function e(t, i, r) {
			var s,
				c = document.createElement("div");
			if ((r && a(c, "guac-keyboard-" + g(r)), i instanceof Array))
				for (a(c, "guac-keyboard-group"), s = 0; s < i.length; s++) e(c, i[s]);
			else if (i instanceof Object) {
				a(c, "guac-keyboard-group");
				var h = Object.keys(i).sort();
				for (s = 0; s < h.length; s++) {
					r = h[s];
					e(c, i[r], r);
				}
			} else if ("number" == typeof i)
				a(c, "guac-keyboard-gap"), o.push(new l(c, i, i));
			else if ("string" == typeof i) {
				var p = i;
				1 === p.length && (p = "0x" + p.charCodeAt(0).toString(16)),
					a(c, "guac-keyboard-key-container");
				var v = document.createElement("div");
				v.className = "guac-keyboard-key guac-keyboard-key-" + g(p);
				var m = n.keys[i];
				if (m)
					for (s = 0; s < m.length; s++) {
						var y = m[s],
							w = document.createElement("div");
						(w.className = "guac-keyboard-cap"), (w.textContent = y.title);
						for (var S = 0; S < y.requires.length; S++) {
							var T = y.requires[S];
							a(w, "guac-keyboard-requires-" + g(T)),
								a(v, "guac-keyboard-uses-" + g(T));
						}
						v.appendChild(w);
					}
				c.appendChild(v), o.push(new l(c, n.layout.keyWidths[i] || 1, 1, !0));
				var E = function (e) {
					e.preventDefault(), 0 === u && f(i, v);
				};
				v.addEventListener(
					"touchstart",
					function (e) {
						e.preventDefault(), (u = n.touchMouseThreshold), d(i, v);
					},
					!0
				),
					v.addEventListener(
						"touchend",
						function (e) {
							e.preventDefault(), (u = n.touchMouseThreshold), f(i, v);
						},
						!0
					),
					v.addEventListener(
						"mousedown",
						function (e) {
							e.preventDefault(), 0 === u && d(i, v);
						},
						!0
					),
					v.addEventListener("mouseup", E, !0),
					v.addEventListener("mouseout", E, !0);
			}
			t.appendChild(c);
		})(p, t.layout);
	}),
	(e.OnScreenKeyboard.Layout = function (e) {
		(this.language = e.language),
			(this.type = e.type),
			(this.keys = e.keys),
			(this.layout = e.layout),
			(this.width = e.width),
			(this.keyWidths = e.keyWidths || {});
	}),
	(e.OnScreenKeyboard.Key = function (e, t) {
		(this.name = t || e.name),
			(this.title = e.title || this.name),
			(this.keysym =
				e.keysym ||
				(function (e) {
					if (!e || 1 !== e.length) return null;
					var t = e.charCodeAt(0);
					return t >= 0 && t <= 255
						? t
						: t >= 256 && t <= 1114111
						? 16777216 | t
						: null;
				})(this.title)),
			(this.modifier = e.modifier),
			(this.requires = e.requires || []);
	}),
	((e = e || {}).OutputStream = function (e, t) {
		var n = this;
		(this.index = t),
			(this.onack = null),
			(this.sendBlob = function (t) {
				e.sendBlob(n.index, t);
			}),
			(this.sendEnd = function () {
				e.endStream(n.index);
			});
	}),
	((e = e || {}).Parser = function () {
		var e = this,
			t = "",
			n = [],
			i = -1,
			r = 0;
		(this.receive = function (o) {
			for (
				r > 4096 && i >= r && ((t = t.substring(r)), (i -= r), (r = 0)), t += o;
				i < t.length;

			) {
				if (i >= r) {
					var a = t.substring(r, i),
						s = t.substring(i, i + 1);
					if ((n.push(a), ";" == s)) {
						var u = n.shift();
						null != e.oninstruction && e.oninstruction(u, n), (n.length = 0);
					} else if ("," != s) throw new Error("Illegal terminator.");
					r = i + 1;
				}
				var l = t.indexOf(".", r);
				if (-1 == l) {
					r = t.length;
					break;
				}
				var c = parseInt(t.substring(i + 1, l));
				if (isNaN(c))
					throw new Error("Non-numeric character in element length.");
				i = (r = l + 1) + c;
			}
		}),
			(this.oninstruction = null);
	}),
	((e = e || {}).Position = function (e) {
		(e = e || {}),
			(this.x = e.x || 0),
			(this.y = e.y || 0),
			(this.fromClientPosition = function (e, t, n) {
				(this.x = t - e.offsetLeft), (this.y = n - e.offsetTop);
				for (var i = e.offsetParent; i && i !== document.body; )
					(this.x -= i.offsetLeft - i.scrollLeft),
						(this.y -= i.offsetTop - i.scrollTop),
						(i = i.offsetParent);
				if (i) {
					var r =
							document.body.scrollLeft || document.documentElement.scrollLeft,
						o = document.body.scrollTop || document.documentElement.scrollTop;
					(this.x -= i.offsetLeft - r), (this.y -= i.offsetTop - o);
				}
			});
	}),
	(e.Position.fromClientPosition = function (t, n, i) {
		var r = new e.Position();
		return r.fromClientPosition(t, n, i), r;
	}),
	((e = e || {}).RawAudioFormat = function (e) {
		(this.bytesPerSample = e.bytesPerSample),
			(this.channels = e.channels),
			(this.rate = e.rate);
	}),
	(e.RawAudioFormat.parse = function (t) {
		var n,
			i = null,
			r = 1;
		if ("audio/L8;" === t.substring(0, 9)) (t = t.substring(9)), (n = 1);
		else {
			if ("audio/L16;" !== t.substring(0, 10)) return null;
			(t = t.substring(10)), (n = 2);
		}
		for (var o = t.split(","), a = 0; a < o.length; a++) {
			var s = o[a],
				u = s.indexOf("=");
			if (-1 === u) return null;
			var l = s.substring(0, u),
				c = s.substring(u + 1);
			switch (l) {
				case "channels":
					r = parseInt(c);
					break;
				case "rate":
					i = parseInt(c);
					break;
				default:
					return null;
			}
		}
		return null === i
			? null
			: new e.RawAudioFormat({ bytesPerSample: n, channels: r, rate: i });
	}),
	((e = e || {}).SessionRecording = function (t) {
		var n,
			i = this,
			r = null,
			o = 262144,
			a = [],
			s = 0,
			u = new e.SessionRecording._PlaybackTunnel(),
			l = new e.Client(u),
			c = -1,
			h = null,
			d = null,
			f = null,
			p = 0,
			v = 0,
			g = !1,
			m = null,
			y = function (t, r, a) {
				if (!g || t !== n) {
					var s = new e.Parser();
					s.oninstruction = r;
					var u = 0,
						l = new FileReader(),
						c = function () {
							if (!g || t !== n) {
								if (2 === l.readyState)
									try {
										s.receive(l.result);
									} catch (e) {
										return void (i.onerror && i.onerror(e.message));
									}
								if (u >= t.size) a && a();
								else {
									var e = t.slice(u, u + o);
									(u += e.size), l.readAsText(e);
								}
							}
						};
					(l.onload = c), c();
				}
			},
			w = function (e) {
				for (var t = e.length, n = t + 3; t >= 10; )
					n++, (t = Math.floor(t / 10));
				return n;
			};
		l.connect(), l.getDisplay().showCursor(!1);
		var S = function (t, n) {
				v += w(t);
				for (var r = 0; r < n.length; r++) v += w(n[r]);
				if ("sync" === t) {
					var o = parseInt(n[0]),
						u = new e.SessionRecording._Frame(o, p, v);
					a.push(u),
						(p = v),
						(1 === a.length ||
							(v - a[s].start >= 16384 && o - a[s].timestamp >= 5e3)) &&
							((u.keyframe = !0), (s = a.length - 1)),
						i.onprogress && i.onprogress(i.getDuration(), v);
				}
			},
			T = function () {
				i.onload && i.onload();
			};
		if (t instanceof Blob) y(n, S, T);
		else {
			(r = t), (n = new Blob());
			var E = !1,
				I = "";
			(r.oninstruction = function (e, t) {
				(I += e.length + "." + e),
					t.forEach(function (e) {
						I += "," + e.length + "." + e;
					}),
					(I += ";").length >= o && ((n = new Blob([n, I])), (I = "")),
					S(e, t);
			}),
				(r.onerror = function (e) {
					(E = !0), i.onerror && i.onerror(e.message);
				}),
				(r.onstatechange = function (t) {
					t === e.Tunnel.State.CLOSED &&
						(I.length && ((n = new Blob([n, I])), (I = "")), E || T());
				});
		}
		var b = function (e) {
				return 0 === a.length ? 0 : e - a[0].timestamp;
			},
			C = function e(t, n, i) {
				if (t === n) return t;
				var r = Math.floor((t + n) / 2),
					o = b(a[r].timestamp);
				return i < o && r > t
					? e(t, r - 1, i)
					: i > o && r < n
					? e(r + 1, n, i)
					: r;
			},
			k = function (e, t, r) {
				A();
				for (
					var o = (f = { aborted: !1 }),
						s = e,
						h = function r() {
							i.onseek && c > s && i.onseek(b(a[c].timestamp), c - s, e - s),
								o.aborted ||
									(c < e
										? (function (e, t) {
												var i = a[e];
												y(
													n.slice(i.start, i.end),
													function (e, t) {
														u.receiveInstruction(e, t);
													},
													function () {
														i.keyframe &&
															!i.clientState &&
															l.exportState(function (e) {
																i.clientState = new Blob([JSON.stringify(e)]);
															}),
															(c = e),
															t && t();
													}
												);
										  })(c + 1, r)
										: t());
						},
						d = function () {
							var e = r ? Math.max(r - new Date().getTime(), 0) : 0;
							e ? window.setTimeout(h, e) : h();
						};
					s >= 0;
					s--
				) {
					var p = a[s];
					if (s === c) break;
					if (p.clientState)
						return void p.clientState.text().then(function (e) {
							l.importState(JSON.parse(e)), (c = s), d();
						});
				}
				d();
			},
			A = function () {
				f && ((f.aborted = !0), (f = null));
			},
			L = function e() {
				if (c + 1 < a.length) {
					var t = a[c + 1].timestamp - h + d;
					k(
						c + 1,
						function () {
							e();
						},
						t
					);
				} else i.pause();
			};
		(this.onload = null),
			(this.onerror = null),
			(this.onabort = null),
			(this.onprogress = null),
			(this.onplay = null),
			(this.onpause = null),
			(this.onseek = null),
			(this.connect = function (e) {
				r && r.connect(e);
			}),
			(this.disconnect = function () {
				r && r.disconnect();
			}),
			(this.abort = function () {
				g || ((g = !0), i.onabort && i.onabort(), r && r.disconnect());
			}),
			(this.getDisplay = function () {
				return l.getDisplay();
			}),
			(this.isPlaying = function () {
				return !!h;
			}),
			(this.getPosition = function () {
				return -1 === c ? 0 : b(a[c].timestamp);
			}),
			(this.getDuration = function () {
				return 0 === a.length ? 0 : b(a[a.length - 1].timestamp);
			}),
			(this.play = function () {
				if (!i.isPlaying() && c + 1 < a.length) {
					i.onplay && i.onplay();
					var e = a[c + 1];
					(h = e.timestamp), (d = new Date().getTime()), L();
				}
			}),
			(this.seek = function (e, t) {
				if (0 !== a.length) {
					i.cancel();
					var n = i.isPlaying();
					i.pause(),
						(m = function () {
							(m = null), n && (i.play(), (n = null)), t && t();
						}),
						k(C(0, a.length - 1, e), m);
				}
			}),
			(this.cancel = function () {
				m && (A(), m());
			}),
			(this.pause = function () {
				A(),
					i.isPlaying() && (i.onpause && i.onpause(), (h = null), (d = null));
			});
	}),
	(e.SessionRecording._Frame = function (e, t, n) {
		(this.keyframe = !1),
			(this.timestamp = e),
			(this.start = t),
			(this.end = n),
			(this.clientState = null);
	}),
	(e.SessionRecording._PlaybackTunnel = function () {
		var e = this;
		(this.connect = function (e) {}),
			(this.sendMessage = function (e) {}),
			(this.disconnect = function () {}),
			(this.receiveInstruction = function (t, n) {
				e.oninstruction && e.oninstruction(t, n);
			});
	}),
	((e = e || {}).Status = function (e, t) {
		var n = this;
		(this.code = e),
			(this.message = t),
			(this.isError = function () {
				return n.code < 0 || n.code > 255;
			});
	}),
	(e.Status.Code = {
		SUCCESS: 0,
		UNSUPPORTED: 256,
		SERVER_ERROR: 512,
		SERVER_BUSY: 513,
		UPSTREAM_TIMEOUT: 514,
		UPSTREAM_ERROR: 515,
		RESOURCE_NOT_FOUND: 516,
		RESOURCE_CONFLICT: 517,
		RESOURCE_CLOSED: 518,
		UPSTREAM_NOT_FOUND: 519,
		UPSTREAM_UNAVAILABLE: 520,
		SESSION_CONFLICT: 521,
		SESSION_TIMEOUT: 522,
		SESSION_CLOSED: 523,
		CLIENT_BAD_REQUEST: 768,
		CLIENT_UNAUTHORIZED: 769,
		CLIENT_FORBIDDEN: 771,
		CLIENT_TIMEOUT: 776,
		CLIENT_OVERRUN: 781,
		CLIENT_BAD_TYPE: 783,
		CLIENT_TOO_MANY: 797,
	}),
	(e.Status.Code.fromHTTPCode = function (t) {
		switch (t) {
			case 400:
				return e.Status.Code.CLIENT_BAD_REQUEST;
			case 403:
				return e.Status.Code.CLIENT_FORBIDDEN;
			case 404:
				return e.Status.Code.RESOURCE_NOT_FOUND;
			case 429:
				return e.Status.Code.CLIENT_TOO_MANY;
			case 503:
				return e.Status.Code.SERVER_BUSY;
		}
		return e.Status.Code.SERVER_ERROR;
	}),
	(e.Status.Code.fromWebSocketCode = function (t) {
		switch (t) {
			case 1e3:
				return e.Status.Code.SUCCESS;
			case 1006:
			case 1015:
				return e.Status.Code.UPSTREAM_NOT_FOUND;
			case 1001:
			case 1012:
			case 1013:
			case 1014:
				return e.Status.Code.UPSTREAM_UNAVAILABLE;
		}
		return e.Status.Code.SERVER_ERROR;
	}),
	((e = e || {}).StringReader = function (t) {
		var n = this,
			i = new e.UTF8Parser(),
			r = new e.ArrayBufferReader(t);
		(r.ondata = function (e) {
			var t = i.decode(e);
			n.ontext && n.ontext(t);
		}),
			(r.onend = function () {
				n.onend && n.onend();
			}),
			(this.ontext = null),
			(this.onend = null);
	}),
	((e = e || {}).StringWriter = function (t) {
		var n = this,
			i = new e.ArrayBufferWriter(t),
			r = new Uint8Array(8192),
			o = 0;
		function a(e) {
			var t, n;
			if (e <= 127) (t = 0), (n = 1);
			else if (e <= 2047) (t = 192), (n = 2);
			else if (e <= 65535) (t = 224), (n = 3);
			else {
				if (!(e <= 2097151)) return void a(65533);
				(t = 240), (n = 4);
			}
			!(function (e) {
				if (o + e >= r.length) {
					var t = new Uint8Array(2 * (o + e));
					t.set(r), (r = t);
				}
				o += e;
			})(n);
			for (var i = o - 1, s = 1; s < n; s++)
				(r[i--] = 128 | (63 & e)), (e >>= 6);
			r[i] = t | e;
		}
		(i.onack = function (e) {
			n.onack && n.onack(e);
		}),
			(this.sendText = function (e) {
				e.length &&
					i.sendData(
						(function (e) {
							for (var t = 0; t < e.length; t++) a(e.charCodeAt(t));
							if (o > 0) {
								var n = r.subarray(0, o);
								return (o = 0), n;
							}
						})(e)
					);
			}),
			(this.sendEnd = function () {
				i.sendEnd();
			}),
			(this.onack = null);
	}),
	((e = e || {}).Touch = function (t) {
		e.Event.Target.call(this);
		var n = this,
			i = Math.floor(16 * window.devicePixelRatio);
		(this.touches = {}),
			(this.activeTouches = 0),
			t.addEventListener(
				"touchstart",
				function (r) {
					for (var o = 0; o < r.changedTouches.length; o++) {
						var a = r.changedTouches[o],
							s = a.identifier;
						if (!n.touches[s]) {
							var u = (n.touches[s] = new e.Touch.State({
								id: s,
								radiusX: a.radiusX || i,
								radiusY: a.radiusY || i,
								angle: a.angle || 0,
								force: a.force || 1,
							}));
							n.activeTouches++,
								u.fromClientPosition(t, a.clientX, a.clientY),
								n.dispatch(new e.Touch.Event("touchmove", r, u));
						}
					}
				},
				!1
			),
			t.addEventListener(
				"touchmove",
				function (r) {
					for (var o = 0; o < r.changedTouches.length; o++) {
						var a = r.changedTouches[o],
							s = a.identifier,
							u = n.touches[s];
						u &&
							(a.force && (u.force = a.force),
							(u.angle = a.angle || 0),
							(u.radiusX = a.radiusX || i),
							(u.radiusY = a.radiusY || i),
							u.fromClientPosition(t, a.clientX, a.clientY),
							n.dispatch(new e.Touch.Event("touchmove", r, u)));
					}
				},
				!1
			),
			t.addEventListener(
				"touchend",
				function (i) {
					for (var r = 0; r < i.changedTouches.length; r++) {
						var o = i.changedTouches[r],
							a = o.identifier,
							s = n.touches[a];
						s &&
							(delete n.touches[a],
							n.activeTouches--,
							(s.force = 0),
							s.fromClientPosition(t, o.clientX, o.clientY),
							n.dispatch(new e.Touch.Event("touchend", i, s)));
					}
				},
				!1
			);
	}),
	(e.Touch.State = function (t) {
		(t = t || {}),
			e.Position.call(this, t),
			(this.id = t.id || 0),
			(this.radiusX = t.radiusX || 0),
			(this.radiusY = t.radiusY || 0),
			(this.angle = t.angle || 0),
			(this.force = t.force || 1);
	}),
	(e.Touch.Event = function (t, n, i) {
		e.Event.DOMEvent.call(this, t, [n]), (this.state = i);
	}),
	((e = e || {}).Tunnel = function () {
		(this.connect = function (e) {}),
			(this.disconnect = function () {}),
			(this.sendMessage = function (e) {}),
			(this.setState = function (e) {
				e !== this.state &&
					((this.state = e), this.onstatechange && this.onstatechange(e));
			}),
			(this.setUUID = function (e) {
				(this.uuid = e), this.onuuid && this.onuuid(e);
			}),
			(this.isConnected = function () {
				return (
					this.state === e.Tunnel.State.OPEN ||
					this.state === e.Tunnel.State.UNSTABLE
				);
			}),
			(this.state = e.Tunnel.State.CLOSED),
			(this.receiveTimeout = 15e3),
			(this.unstableThreshold = 1500),
			(this.uuid = null),
			(this.onuuid = null),
			(this.onerror = null),
			(this.onstatechange = null),
			(this.oninstruction = null);
	}),
	(e.Tunnel.INTERNAL_DATA_OPCODE = ""),
	(e.Tunnel.State = { CONNECTING: 0, OPEN: 1, CLOSED: 2, UNSTABLE: 3 }),
	(e.HTTPTunnel = function (t, n, i) {
		var r = this,
			o = t + "?connect",
			a = t + "?read:",
			s = t + "?write:",
			u = 1,
			l = !1,
			c = "",
			h = !!n,
			d = null,
			f = null,
			p = null,
			v = i || {},
			g = "Guacamole-Tunnel-Token",
			m = null;
		function y(e, t) {
			for (var n in t) e.setRequestHeader(n, t[n]);
		}
		var w = function () {
			window.clearTimeout(d),
				window.clearTimeout(f),
				r.state === e.Tunnel.State.UNSTABLE && r.setState(e.Tunnel.State.OPEN),
				(d = window.setTimeout(function () {
					S(new e.Status(e.Status.Code.UPSTREAM_TIMEOUT, "Server timeout."));
				}, r.receiveTimeout)),
				(f = window.setTimeout(function () {
					r.setState(e.Tunnel.State.UNSTABLE);
				}, r.unstableThreshold));
		};
		function S(t) {
			window.clearTimeout(d),
				window.clearTimeout(f),
				window.clearInterval(p),
				r.state !== e.Tunnel.State.CLOSED &&
					(t.code !== e.Status.Code.SUCCESS &&
						r.onerror &&
						((r.state !== e.Tunnel.State.CONNECTING &&
							t.code === e.Status.Code.RESOURCE_NOT_FOUND) ||
							r.onerror(t)),
					(l = !1),
					r.setState(e.Tunnel.State.CLOSED));
		}
		function T() {
			if (r.isConnected())
				if (c.length > 0) {
					l = !0;
					var e = new XMLHttpRequest();
					e.open("POST", s + r.uuid),
						(e.withCredentials = h),
						y(e, v),
						e.setRequestHeader("Content-type", "application/octet-stream"),
						e.setRequestHeader(g, m),
						(e.onreadystatechange = function () {
							4 === e.readyState && (w(), 200 !== e.status ? E(e) : T());
						}),
						e.send(c),
						(c = "");
				} else l = !1;
		}
		function E(t) {
			var n = parseInt(t.getResponseHeader("Guacamole-Status-Code"));
			if (n) {
				var i = t.getResponseHeader("Guacamole-Error-Message");
				S(new e.Status(n, i));
			} else
				t.status
					? S(new e.Status(e.Status.Code.fromHTTPCode(t.status), t.statusText))
					: S(new e.Status(e.Status.Code.UPSTREAM_NOT_FOUND));
		}
		function I(e) {
			var t = null,
				n = null,
				i = 0,
				o = -1,
				a = 0,
				s = new Array();
			function l() {
				if (r.isConnected()) {
					if (!(e.readyState < 2)) {
						var i;
						try {
							i = e.status;
						} catch (e) {
							i = 200;
						}
						if (
							(n || 200 !== i || (n = C()),
							3 === e.readyState || 4 === e.readyState)
						) {
							if (
								(w(),
								1 === u &&
									(3 !== e.readyState || t
										? 4 === e.readyState && t && clearInterval(t)
										: (t = setInterval(l, 30))),
								0 === e.status)
							)
								return void r.disconnect();
							if (200 !== e.status) return void E(e);
							var c;
							try {
								c = e.responseText;
							} catch (e) {
								return;
							}
							for (; o < c.length; ) {
								if (o >= a) {
									var h = c.substring(a, o),
										d = c.substring(o, o + 1);
									if ((s.push(h), ";" === d)) {
										var f = s.shift();
										r.oninstruction && r.oninstruction(f, s), (s.length = 0);
									}
									a = o + 1;
								}
								var p = c.indexOf(".", a);
								if (-1 === p) {
									a = c.length;
									break;
								}
								var v = parseInt(c.substring(o + 1, p));
								if (0 === v) {
									t && clearInterval(t),
										(e.onreadystatechange = null),
										e.abort(),
										n && I(n);
									break;
								}
								o = (a = p + 1) + v;
							}
						}
					}
				} else null !== t && clearInterval(t);
			}
			(e.onreadystatechange =
				1 === u
					? function () {
							3 === e.readyState &&
								++i >= 2 &&
								((u = 0), (e.onreadystatechange = l)),
								l();
					  }
					: l),
				l();
		}
		this.sendMessage = function () {
			if (r.isConnected() && 0 !== arguments.length) {
				for (var e = n(arguments[0]), t = 1; t < arguments.length; t++)
					e += "," + n(arguments[t]);
				(c += e += ";"), l || T();
			}
			function n(e) {
				var t = new String(e);
				return t.length + "." + t;
			}
		};
		var b = 0;
		function C() {
			var e = new XMLHttpRequest();
			return (
				e.open("GET", a + r.uuid + ":" + b++),
				e.setRequestHeader(g, m),
				(e.withCredentials = h),
				y(e, v),
				e.send(null),
				e
			);
		}
		(this.connect = function (t) {
			w(), r.setState(e.Tunnel.State.CONNECTING);
			var n = new XMLHttpRequest();
			(n.onreadystatechange = function () {
				4 === n.readyState &&
					(200 === n.status
						? (w(),
						  r.setUUID(n.responseText),
						  (m = n.getResponseHeader(g))
								? (r.setState(e.Tunnel.State.OPEN),
								  (p = setInterval(function () {
										r.sendMessage("nop");
								  }, 500)),
								  I(C()))
								: S(new e.Status(e.Status.Code.UPSTREAM_NOT_FOUND)))
						: E(n));
			}),
				n.open("POST", o, !0),
				(n.withCredentials = h),
				y(n, v),
				n.setRequestHeader(
					"Content-type",
					"application/x-www-form-urlencoded; charset=UTF-8"
				),
				n.send(t);
		}),
			(this.disconnect = function () {
				S(new e.Status(e.Status.Code.SUCCESS, "Manually closed."));
			});
	}),
	(e.HTTPTunnel.prototype = new e.Tunnel()),
	(e.WebSocketTunnel = function (t) {
		var n = this,
			i = null,
			r = null,
			o = null,
			a = null,
			s = 0;
		if ("ws:" !== t.substring(0, 3) && "wss:" !== t.substring(0, 4)) {
			var u = { "http:": "ws:", "https:": "wss:" }[window.location.protocol];
			if ("/" === t.substring(0, 1)) t = u + "//" + window.location.host + t;
			else {
				var l = window.location.pathname.lastIndexOf("/"),
					c = window.location.pathname.substring(0, l + 1);
				t = u + "//" + window.location.host + c + t;
			}
		}
		var h = function () {
				var t = new Date().getTime();
				n.sendMessage(e.Tunnel.INTERNAL_DATA_OPCODE, "ping", t), (s = t);
			},
			d = function () {
				window.clearTimeout(r),
					window.clearTimeout(o),
					window.clearTimeout(a),
					n.state === e.Tunnel.State.UNSTABLE &&
						n.setState(e.Tunnel.State.OPEN),
					(r = window.setTimeout(function () {
						f(new e.Status(e.Status.Code.UPSTREAM_TIMEOUT, "Server timeout."));
					}, n.receiveTimeout)),
					(o = window.setTimeout(function () {
						n.setState(e.Tunnel.State.UNSTABLE);
					}, n.unstableThreshold));
				var t = new Date().getTime(),
					i = Math.max(s + 500 - t, 0);
				i > 0 ? (a = window.setTimeout(h, i)) : h();
			};
		function f(t) {
			window.clearTimeout(r),
				window.clearTimeout(o),
				window.clearTimeout(a),
				n.state !== e.Tunnel.State.CLOSED &&
					(t.code !== e.Status.Code.SUCCESS && n.onerror && n.onerror(t),
					n.setState(e.Tunnel.State.CLOSED),
					i.close());
		}
		(this.sendMessage = function (e) {
			if (n.isConnected() && 0 !== arguments.length) {
				for (var t = o(arguments[0]), r = 1; r < arguments.length; r++)
					t += "," + o(arguments[r]);
				(t += ";"), i.send(t);
			}
			function o(e) {
				var t = new String(e);
				return t.length + "." + t;
			}
		}),
			(this.connect = function (r) {
				d(),
					n.setState(e.Tunnel.State.CONNECTING),
					((i = new WebSocket(t + "?" + r, "guacamole")).onopen = function (e) {
						d();
					}),
					(i.onclose = function (t) {
						t.reason
							? f(new e.Status(parseInt(t.reason), t.reason))
							: t.code
							? f(new e.Status(e.Status.Code.fromWebSocketCode(t.code)))
							: f(new e.Status(e.Status.Code.UPSTREAM_NOT_FOUND));
					}),
					(i.onmessage = function (t) {
						d();
						var i,
							r = t.data,
							o = 0,
							a = [];
						do {
							var s = r.indexOf(".", o);
							if (-1 !== s) i = (o = s + 1) + parseInt(r.substring(i + 1, s));
							else
								f(
									new e.Status(
										e.Status.Code.SERVER_ERROR,
										"Incomplete instruction."
									)
								);
							var u = r.substring(o, i),
								l = r.substring(i, i + 1);
							if ((a.push(u), ";" === l)) {
								var c = a.shift();
								null === n.uuid &&
									(c === e.Tunnel.INTERNAL_DATA_OPCODE &&
										1 === a.length &&
										n.setUUID(a[0]),
									n.setState(e.Tunnel.State.OPEN)),
									c !== e.Tunnel.INTERNAL_DATA_OPCODE &&
										n.oninstruction &&
										n.oninstruction(c, a),
									(a.length = 0);
							}
							o = i + 1;
						} while (o < r.length);
					});
			}),
			(this.disconnect = function () {
				f(new e.Status(e.Status.Code.SUCCESS, "Manually closed."));
			});
	}),
	(e.WebSocketTunnel.prototype = new e.Tunnel()),
	(e.ChainedTunnel = function (t) {
		for (var n, i = this, r = [], o = null, a = 0; a < arguments.length; a++)
			r.push(arguments[a]);
		function s(t) {
			(i.disconnect = t.disconnect), (i.sendMessage = t.sendMessage);
			var a = function (n) {
				if (n && n.code === e.Status.Code.UPSTREAM_TIMEOUT)
					return (r = []), null;
				var i = r.shift();
				return (
					i &&
						((t.onerror = null),
						(t.oninstruction = null),
						(t.onstatechange = null),
						s(i)),
					i
				);
			};
			function u() {
				(t.onstatechange = i.onstatechange),
					(t.oninstruction = i.oninstruction),
					(t.onerror = i.onerror),
					t.uuid && i.setUUID(t.uuid),
					(t.onuuid = function (e) {
						i.setUUID(e);
					}),
					(o = t);
			}
			(t.onstatechange = function (t) {
				switch (t) {
					case e.Tunnel.State.OPEN:
						u(), i.onstatechange && i.onstatechange(t);
						break;
					case e.Tunnel.State.CLOSED:
						!a() && i.onstatechange && i.onstatechange(t);
				}
			}),
				(t.oninstruction = function (e, t) {
					u(), i.oninstruction && i.oninstruction(e, t);
				}),
				(t.onerror = function (e) {
					!a(e) && i.onerror && i.onerror(e);
				}),
				t.connect(n);
		}
		this.connect = function (t) {
			n = t;
			var a = o || r.shift();
			a
				? s(a)
				: i.onerror &&
				  i.onerror(e.Status.Code.SERVER_ERROR, "No tunnels to try.");
		};
	}),
	(e.ChainedTunnel.prototype = new e.Tunnel()),
	(e.StaticHTTPTunnel = function (t, n, i) {
		var r = this,
			o = null,
			a = i || {};
		(this.size = null),
			(this.sendMessage = function (e) {}),
			(this.connect = function (i) {
				r.disconnect(), r.setState(e.Tunnel.State.CONNECTING);
				var s = new e.Parser(),
					u = new e.UTF8Parser();
				(s.oninstruction = function (e, t) {
					r.oninstruction && r.oninstruction(e, t);
				}),
					(o = new AbortController()),
					fetch(t, {
						headers: a,
						credentials: n ? "include" : "same-origin",
						signal: o.signal,
					}).then(function (t) {
						if (!t.ok)
							return (
								r.onerror &&
									r.onerror(
										new e.Status(
											e.Status.Code.fromHTTPCode(t.status),
											t.statusText
										)
									),
								void r.disconnect()
							);
						(r.size = t.headers.get("Content-Length")),
							r.setState(e.Tunnel.State.OPEN);
						var n = t.body.getReader();
						n.read().then(function e(t) {
							t.done
								? r.disconnect()
								: (s.receive(u.decode(t.value)), n.read().then(e));
						});
					});
			}),
			(this.disconnect = function () {
				o && (o.abort(), (o = null)), r.setState(e.Tunnel.State.CLOSED);
			});
	}),
	(e.StaticHTTPTunnel.prototype = new e.Tunnel()),
	((e = e || {}).UTF8Parser = function () {
		var e = 0,
			t = 0;
		this.decode = function (n) {
			for (var i = "", r = new Uint8Array(n), o = 0; o < r.length; o++) {
				var a = r[o];
				0 === e
					? 127 == (127 | a)
						? (i += String.fromCharCode(a))
						: 223 == (31 | a)
						? ((t = 31 & a), (e = 1))
						: 239 == (15 | a)
						? ((t = 15 & a), (e = 2))
						: 247 == (7 | a)
						? ((t = 7 & a), (e = 3))
						: (i += "�")
					: 191 == (63 | a)
					? ((t = (t << 6) | (63 & a)),
					  0 === --e && (i += String.fromCharCode(t)))
					: ((e = 0), (i += "�"));
			}
			return i;
		};
	}),
	((e = e || {}).API_VERSION = "1.5.0"),
	((e = e || {}).VideoPlayer = function () {
		this.sync = function () {};
	}),
	(e.VideoPlayer.isSupportedType = function (e) {
		return !1;
	}),
	(e.VideoPlayer.getSupportedTypes = function () {
		return [];
	}),
	(e.VideoPlayer.getInstance = function (e, t, n) {
		return null;
	});
var t = e;
export { t as default };
//# sourceMappingURL=/sm/c096772d5cc5213b09718e94fd46feb85ab647303a38c029a254f16efcafc851.map
