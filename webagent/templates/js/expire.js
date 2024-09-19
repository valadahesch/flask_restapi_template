class Expire {
	constructor() {
    this.expireTimeEl = document.getElementById("expire_time");
		this.anniTimer = null;
		this.expTimer = null
		this.expireTime = 0
		this.handleExpire();
	}

  secondsToHourFormat(seconds) {
    //注意乘以了1000转成毫秒的
    return new Date(seconds * 1000).toISOString().substring(11, 19);
  }

	handleExpire() {
		if (!window.cloud_lab_data?.instance_id) {
			return;
		}

		this.expTimer = setInterval(async () => {
			this._doExpire();
		}, 8000);
		this._doExpire();
	}

	async _doExpire() {
		const self = this
		clearInterval(self.anniTimer);
		self.anniTimer = null
		const result = await fetch(
			`/webagent/api/instance/${window.cloud_lab_data.instance_id}/expire`
		).then((d) => d.json());
		if (result?.code !== 0) {
			clearInterval(self.expTimer);
			self.expTimer = null
			return;
		}
		if (result?.data?.expire) {
			self.expireTime = result.data.expire
			this.expireTimeEl.innerHTML = `${self.secondsToHourFormat(
				self.expireTime
			)}`;

			self.anniTimer = setInterval(() => {
				self.expireTime = self.expireTime - 1
				if(self.expireTime<0){
					self.expireTime = 0
				}
				this.expireTimeEl.innerHTML = `${self.secondsToHourFormat(
					self.expireTime
				)}`;
			}, 1000);
		}
	}
}
