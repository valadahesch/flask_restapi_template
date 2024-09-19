const ConnectMap = {
	DISCONNECTED: 0,
	CONNECTING: 1,
	CONNECTED: 2,
};

const ConnectMapColor = {
	DISCONNECTED: "var(--danger)",
	CONNECTING: "var(--primary)",
	CONNECTED: "var(--success)",
};

const ConnectMapData = {
	DISCONNECTED: "已断开",
	CONNECTING: "连接中",
	CONNECTED: "已连接",
};

const filterStr = `
"SG\\-6000\\-\\S+",0099ccff,00000001
"SG6000\\-\\S*(\\.bin)?$|^uptime\\b|flag.*|\\bday(s)?\\b|hour(s)?|minute(s)?|second(s)?|",00c61aff,00000001
"\\bdeny\\d*\\b|\\bdrop\\d*\\b|\\bfail\\d*\\b|\\bfew\\b|\\bshutdown\\b|\\bunreach\\d*\\b|\\binvalid\\d*\\b|\\bfail\\d*\\b",00ff0000,00000001
"\\binactive\\b|\\berr\\d*\\b|\\bdifferent\\b|\\boff\\b|\\bon$|^remove\\d*\\b|\\bnot\\b|absent\\d*\\b|restart\\d*\\b",00ff0000,00000001
"\\bD\\b[^:]|\\bskip\\d*\\b|\\bno\\d*\\b|\\[DBG\\]|\\bdebug\\d*\\b|\\bcannot\\d*\\b|\\babort\\d*\\b|\\bmissed\\d*\\b|\\bheartbeat\\d*\\b|\\breset\\d*\\b|\\bwatchdog\\d*\\b|\\breboot\\d*\\b|\\brestored\\d*\\b|\\bexpire\\d*\\b|\\bprofiling\\d*\\b|\\btriggerred\\d*\\b",00ff0000,00000001
"\\bwarning\\d*\\b|\\bMemFree\\d*\\b|\\bless\\d*\\b|\\bdying\\d*\\b|\\bdon't\\d*\\b|\\bhasn't\\d*\\b|\\bclear\\d*\\b|\\bunset\\d*\\b|\\bmismatch\\d*\\b|\\bdoesn't\\d*\\b|\\bDidn't\\d*\\b|\\bOffline\\d*\\b|\\bexhaust\\d*\\b|\\bdead\\d*\\b",00ff9933,00000001
"\\bdisable\\d*\\b|\\<down\\>|\\bembedded\\d*\\b|\\bmatch\\d*\\b|\\bnexthop:|\\bbacktrace\\b|\\bdelete\\d*\\b|\\bidentif\\d*\\b|\\brampup\\b|\\bdisconnect\\d*\\b|\\bclose\\d*\\b",00ff9933,00000001
"\\bInBroadcas\\d*\\b|\\bInOversize\\d*\\b|\\bCollisions\\d*\\b|\\bretransmitted\\d*\\b|\\bResend\\d*\\b|\\bwarning\\d*\\b|\\bBad\\d*\\b",00ff9933,00000001
"[7-9][0-9]\\%|100\\%",00ff0000,00000001
"\\b(x)?ethernet\\d+\\/\\d+(\\.\\d+)?",00ffcc99,00000001
"\\baggregate\\d+|\\bredundant\\d+",00d580ff,00000001
"\\btunnel\\d+|\\bloopback\\d+",00d580ff,00000001
"\\bvlan\\d+|\\bvswitchif\\d+",00ffff66,00000001
"((2[0-4]\\d|25[0-5]|[01]?\\d\\d?)\\.){3}(2[0-4]\\d|25[0-5]|[01]?\\d\\d?)",0080bfff,00000001
"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))",003399ff,00000001
`;

const filterReg = /[\s\S]*,00[0-9a-zA-Z]{6},00[0-9a-zA-Z]{6}/;

const filterMap = (() => {
	const result = [];
	const filterArr = filterStr.split("\n").filter((f) => !!f);

	filterArr.forEach((trimContent) => {
		if (filterReg.test(trimContent)) {
			//trim一下，从后往前截断
			const bgColor = trimContent.slice(
				trimContent.length - 8,
				trimContent.length - 1
			);
			const feColor = trimContent.slice(
				trimContent.length - 17,
				trimContent.length - 9
			);
			const reg = trimContent.slice(1, trimContent.length - 19);
			const item = {
				reg,
				feColor,
				bgColor,
			};
			result.push(item);
		}
	});
	return result;
})();

function debounce(func, timeout = 300) {
	let timer;
	return (...args) => {
		clearTimeout(timer);
		timer = setTimeout(() => {
			func.apply(this, args);
		}, timeout);
	};
}

function getTitle(status) {
	return `[${status}][${window.cloud_lab_data?.login_name}][${window.cloud_lab_data?.node_name}][${window.cloud_lab_data?.instance_name}]`;
}


const chalkInstance = new chalk.Chalk({
	level: 3,
});

class Start {
	constructor() {
		this.terminalEl = document.getElementById("terminal");
		this.topBar = document.getElementById("top_bar")
		this.highlightEl = document.getElementById("highlightBtn");
		this.statusEl = document.getElementById("status");
		this.maskEl = document.getElementById("mask");

		this.ws_id = window.cloud_lab_data?.ws_id;
		this.node_id = window.cloud_lab_data?.node_id;
		this.state = ConnectMap.DISCONNECTED;
		this.term = this.initTerm();
		this.fit();
		this.wsUrl = `${window.cloud_lab_data?.ws_url}/cloud_lab/cli?ws_id=${this.ws_id}&node_id=${this.node_id}`;
		this.ws = this.initWs();

		this.listenEvent();
	}

	initTerm() {
		const term = new Terminal({
			convertEol: true,
			scrollback: 9999999,
			cursorStyle: "underline",
			cursorBlink: true,
			fontFamily: "Monaco, Menlo, Consolas, 'Courier New', monospace",
			fontWeight: "normal",
			rightClickSelectsWord: true,
			theme: {
				foreground: "#00ff00",
				background: "#000000",
			},
		});
		return term;
	}

	fit() {
		const self = this;
		const fitAddon = new FitAddon.FitAddon();
		self.term?.loadAddon(fitAddon);
		self.fitAddon = fitAddon;

		setTimeout(() => {
			self.fitAddon?.fit();
		}, 800);

		self.term?.focus();

		//节流解决fit控制台报错
		//https://github.com/xtermjs/xterm.js/issues/3118
		window.addEventListener(
			"resize",
			debounce(() => {
				self.fitAddon?.fit();
			}, 50)
		);
	}

	initWs() {
		if (!this.ws_id) {
			return;
		}
		const terminalEl = this.terminalEl;
		const ws = new WebSocket(this.wsUrl);
		this.updateStatus(ConnectMap.CONNECTING);

		ws.onopen = () => {
			this.updateStatus(ConnectMap.CONNECTED);

			this.term.open(terminalEl);
			this.term.focus();

			this.term.onData((data) => {
				if (this.state === ConnectMap.CONNECTED) {
					this.ws.send(data);
				} else {
					this.state = ConnectMap.CONNECTING;
				}
			});
		};
		ws.onmessage = (evt) => {
			const data = this.highlight((evt?.data || "").toString());
			this.term.write(data);
			// console.log("接收到消息", evt?.data, typeof evt?.data);
		};

		ws.onerror = function (e) {
			console.error(e);
		};

		ws.onclose = function (e) {
			this.updateStatus(ConnectMap.DISCONNECTED);
			this.term?.write("\r\n连接已断开...\r\n");
			setTimeout(() => {
				this.term?.dispose();
			}, 1000);
		};
		return ws;
	}

	updateStatus(status) {
		this.state = status;
		const statusMap = Object.entries(ConnectMap).find(
			(c) => c[1] === status
		)[0];
		const statusText = ConnectMapData[statusMap];
		const statusColor = ConnectMapColor[statusMap];
		this.statusEl.innerHTML = `状态：<span style="color:${statusColor}">${statusText}</span>`;
		document.title = getTitle(statusText);
	}

	highlight(data) {
		if (this.highlightEl?.checked) {
			filterMap.forEach((item) => {
				let color1 = "#000001";
				const reg = new RegExp(item.reg, "gmi")
				data = data.replaceAll(reg, (sub) => {
					if (!sub) {
						return sub;
					}
					if (!!sub && sub.match(reg)) {
						// console.log("匹配上", sub, color1, item);
						color1 = item.feColor.replace("00", "#");
					}
					return chalkInstance.hex(color1)(sub);
				});
			});
		}
		return data;
	}

	listenEvent() {
		this.maskEl.addEventListener("click", (e) => {
			this.maskEl.style.display="none";
			this.term.focus()
		})
		this.topBar.addEventListener("click", ()=> {
			this.maskEl.style.display="flex";
		})
	}
}

$(function () {
	new Start();
	new Expire();
});
