
export const Tools = {};
// import { getToken } from '@/utils/auth'
Tools.isEmpty = function(obj) {
  if (typeof obj == "undefined" || obj == null || obj == "") {
    return true;
  } else {
    return false;
  }
};
Tools.isPhone = function(str) {
  var reg = /^1[3456789]\d{9}$/;
  return reg.test(str);
}
  Tools.verifyID = function(str) {
    var reg = /^[1-9][0-9]{5}(19|20)[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|30|31)|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}([0-9]|x|X)$/;
    return reg.test(str);
  }
  Tools.isMobileUserAgent = function() {
    // 判断是pc端还是h5端
    return /iphone|ipod|android|windows.*phone|blackberry.*mobile/i.test(
      window.navigator.userAgent.toLowerCase()
    );
  };
  Tools.getDate = function(time) {
    let date = new Date(time);
    var Y = date.getFullYear() + "-";
    var M =
      (date.getMonth() + 1 < 10
        ? "0" + (date.getMonth() + 1)
        : date.getMonth() + 1) + "-";
    var D = (date.getDate() < 10 ? "0" + date.getDate() : date.getDate());
    return Y + M + D;
  };
//打开摄像头
Tools.getCompetence = function(that, videoId, cancasId) {
  //打开摄像头
  console.log("调用摄像头");
  var _this = that;
  _this.thisCancas = document.getElementById(cancasId);
  console.log("_this.thisCancas", _this.thisCancas);
  _this.thisContext = _this.thisCancas.getContext("2d");
  _this.thisVideo = document.getElementById(videoId);
  _this.thisVideo.style.display = "block";
  // 获取媒体属性，旧版本浏览器可能不支持mediaDevices，我们首先设置一个空对象
  if (navigator.mediaDevices === undefined) {
    navigator.mediaDevices = {};
  }
  // 一些浏览器实现了部分mediaDevices，我们不能只分配一个对象
  // 使用getUserMedia，因为它会覆盖现有的属性。
  // 这里，如果缺少getUserMedia属性，就添加它。
  if (navigator.mediaDevices.getUserMedia === undefined) {
    navigator.mediaDevices.getUserMedia = function(constraints) {
      // 首先获取现存的getUserMedia(如果存在)
      var getUserMedia =
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.getUserMedia;
      // 有些浏览器不支持，会返回错误信息
      // 保持接口一致
      if (!getUserMedia) {
        //不存在则报错
        return Promise.reject(
          new Error("getUserMedia is not implemented in this browser")
        );
      }
      // 否则，使用Promise将调用包装到旧的navigator.getUserMedia
      return new Promise(function(resolve, reject) {
        getUserMedia.call(navigator, constraints, resolve, reject);
      });
    };
  }
  var constraints = {
    audio: false,
    video: {
      width: that.videoWidth,
      height: that.videoHeight,
      transform: "scaleX(-1)"
    }
  };
  navigator.mediaDevices
    .getUserMedia(constraints)
    .then(function(stream) {
      // 旧的浏览器可能没有srcObject
      if ("srcObject" in _this.thisVideo) {
        _this.thisVideo.srcObject = stream;
      } else {
        // 避免在新的浏览器中使用它，因为它正在被弃用。
        _this.thisVideo.src = window.URL.createObjectURL(stream);
      }
      _this.thisVideo.onloadedmetadata = function(e) {
        _this.thisVideo.play();
      };
    })
    .catch(err => {
      console.log(err);
    });
}
  // 关闭摄像头
  Tools.stopNavigator = function() {
    this.thisVideo.srcObject.getTracks()[0].stop();
  }
  Tools.dataURLtoFile = function(dataurl, filename) {
    var arr = dataurl.split(",");
    var mime = arr[0].match(/:(.*?);/)[1];
    var bstr = atob(arr[1]);
    var n = bstr.length;
    var u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    //转换成file对象
    return new File([u8arr], filename, { type: mime });
    //转换成成blob对象
    //return new Blob([u8arr],{type:mime});
  }
  //拍照
  Tools.takePhoto = function(that) {
    var _this = that;
    // canvas画图
    _this.thisContext.drawImage(
      _this.thisVideo,
      0,
      0,
      _this.videoWidth,
      _this.videoHeight
    );
    // 获取图片base64链接
    var image = _this.thisCancas.toDataURL("image/png");
    _this.imgSrc = image; //赋值并预览图片
    // _this.visitorInfo.image = Tools.dataURLtoFile(image,'file')
    return Tools.dataURLtoFile(image, "file.png");
  }
  //上传图片格式
  Tools.beforeAvatarUpload = function(file) {
    let pic = file.name.substring(file.name.lastIndexOf(".") + 1);
    let ext = pic.toLowerCase();
    let flag = false;
    if (ext == "png" || ext == "jpg" || ext == "jpeg") {
      flag = true;
    }
    return flag;
  };
//rtsp视频播放
Tools.streamedian = function(Vid, url, that) {
  // url =
  //   "rtsp://admin:abcdef00@hlstest.tpddns.cn:10554/Streaming/Channels/102";
  let errHandler = function(err) {};

  var playerOptions = {
    socket: "ws://148.70.230.200:9640/ws/",
    redirectNativeMediaErrors: true,
    bufferDuration: 30,
    errorHandler: errHandler
  };

  var html5Player = document.getElementById(Vid);
  html5Player.src = url;
  that.playerRTSP = Streamedian.player(Vid, playerOptions);

  var nativePlayer = document.getElementById(Vid);
  nativePlayer.addEventListener("play", function() {
    //监听播放
    console.log("开始播放");
    console.log(nativePlayer.currentTime, nativePlayer.buffered.end(0));
    setTimeout(function() {
      nativePlayer.currentTime = nativePlayer.buffered.end(0);
    }, 500);
  });
  if (!!window.chrome) {
    document.addEventListener("visibilitychange", function() {
      if (document.visibilityState === "hidden") {
        nativePlayer.pause();
      } else {
        setTimeout(function() {
          nativePlayer.currentTime = nativePlayer.buffered.end(0);
        }, 3000); // Delay for a few seconds is required for the player has time to update the timeline.
      }
    });
  }
}
  Tools.destroyRTSP = function(that) {
    that.playerRTSP.destroy();
    that.playerRTSP = null;
  }
  //压缩图片，改变图片方向
  Tools.getImgData = function(img, dir, next) {
    var image = new Image();
    image.src = img;
    image.onload = function() {
      var degree = 0,
        drawWidth,
        drawHeight,
        width,
        height;
      drawWidth = this.width;
      drawHeight = this.height;

      //以下改变一下图片大小
      var maxSide = Math.max(drawWidth, drawHeight);
      if (maxSide > 400) {
        var minSide = Math.min(drawWidth, drawHeight);
        minSide = (minSide / maxSide) * 400;
        maxSide = 400;
        if (drawWidth > drawHeight) {
          drawWidth = maxSide;
          drawHeight = minSide;
        } else {
          drawWidth = minSide;
          drawHeight = maxSide;
        }
      }
      var canvas = document.createElement("canvas");

      canvas.width = drawWidth;
      canvas.height = drawHeight;
      width = drawWidth;
      height = drawHeight;
      var context = canvas.getContext("2d");
      if (dir.Orientation && dir.Orientation != 1) {
        switch (dir.Orientation) {
          case 3:
            context.rotate(Math.PI);
            context.drawImage(
              this,
              -drawWidth,
              -drawHeight,
              drawWidth,
              drawHeight
            );
            break;
          case 6:
            if (width > height) {
              canvas.width = height;
              canvas.height = width;
              context.rotate(Math.PI / 2);
              context.drawImage(this, 0, -drawHeight, drawWidth, drawHeight);
            } else {
              context.drawImage(this, 0, 0, drawWidth, drawHeight);
            }
            break;
          case 8:
            canvas.width = drawHeight;
            canvas.height = drawWidth;
            context.rotate((3 * Math.PI) / 2);
            context.drawImage(this, -drawWidth, 0, drawWidth, drawHeight);
            break;
        }
      } else {
        context.drawImage(this, 0, 0, drawWidth, drawHeight);
      }
      next(canvas.toDataURL("image/png", 0.8));
    };
  };
Tools.getParam = function(key, strURL) {
  strURL = strURL || window.location.search;
  return new RegExp("(^|\\?|&)" + key + "=([^&]*)(\\s|&|$)", "i").test(strURL)
    ? decodeURIComponent(RegExp.$2.replace(/\+/g, " "))
    : "";
};
Tools.handleClickItem = function(that) {
  // 获取遮罩层dom
  that.$nextTick(() => {
    let domImageMask = document.querySelector(".el-image-viewer__mask");
    console.log("domImageMask", domImageMask);
    if (!domImageMask) {
      return;
    }
    domImageMask.addEventListener("click", () => {
      // 点击遮罩层时调用关闭按钮的 click 事件
      document.querySelector(".el-image-viewer__close").click();
    });
  });
}
  Tools.getImgList = function(item, index) {
    let arr = [];
    let i = 0;
    for (i; i < item.length; i++) {
      arr.push(item[i + index]);
      if (i + index >= item.length - 1) {
        index = 0 - (i + 1);
      }
    }
    return arr;
  }
  Tools.format = time => {
    let ymd = "";
    let mouth =
      time.getMonth() + 1 >= 10
        ? time.getMonth() + 1
        : "0" + (time.getMonth() + 1);
    let day = time.getDate() >= 10 ? time.getDate() : "0" + time.getDate();
    ymd += time.getFullYear() + "-"; // 获取年份。
    ymd += mouth + "-"; // 获取月份。
    ymd += day; // 获取日。
    return ymd; // 返回日期。
  };
Tools.timestampToTime = function(timestamp) {
  var date = new Date(timestamp); //时间戳为10位需*1000，时间戳为13位的话不需乘1000
  var Y = date.getFullYear() + "年";
  var M =
    (date.getMonth() + 1 < 10
      ? "0" + (date.getMonth() + 1)
      : date.getMonth() + 1) + "月";
  var D =
    (date.getDate() < 10 ? "0" + date.getDate() : date.getDate()) + "日  ";
  var h =
    (date.getHours() < 10 ? "0" + date.getHours() : date.getHours()) + ":";
  var m =
    (date.getMinutes() < 10 ? "0" + date.getMinutes() : date.getMinutes()) +
    ":";
  var s = date.getSeconds() < 10 ? "0" + date.getSeconds() : date.getSeconds();
  return Y + M + D + h + m + s;
};
Tools.getAllDate = (start, end) => {
  //开始时间结束时间计算日期
  let dateArr = [];
  let startArr = start.split("-");
  let endArr = end.split("-");
  let db = new Date();
  db.setUTCFullYear(startArr[0], startArr[1] - 1, startArr[2]);
  let de = new Date();
  de.setUTCFullYear(endArr[0], endArr[1] - 1, endArr[2]);
  let unixDb = db.getTime();
  let unixDe = de.getTime();
  let stamp;
  const oneDay = 24 * 60 * 60 * 1000;
  for (stamp = unixDb; stamp <= unixDe; ) {
    dateArr.push(Tools.format(new Date(parseInt(stamp))));
    stamp = stamp + oneDay;
  }
  console.log("日期", dateArr);
  return dateArr;
};
Tools.getDate = function(time) {
  let date = new Date(time);
  var Y = date.getFullYear() + "-";
  var M =
    (date.getMonth() + 1 < 10
      ? "0" + (date.getMonth() + 1)
      : date.getMonth() + 1) + "-";
  var D = (date.getDate() < 10 ? "0" + date.getDate() : date.getDate()) + "  ";
  return Y + M + D;
};
Tools.getDateZ = function(time) {
  let date = new Date(time);
  var Y = date.getFullYear() + "年";
  var M =
    (date.getMonth() + 1 < 10
      ? "0" + (date.getMonth() + 1)
      : date.getMonth() + 1) + "月";
  var D = (date.getDate() < 10 ? "0" + date.getDate() : date.getDate()) + "日";
  return Y + M + D;
};
Tools.exportExcel = function(urldata, data, name, that) {
  let url;
  that.loading = true;
  if (window.location.protocol == "http:") {
    url = process.env.VUE_APP_BASE_API;
  } else {
    url = process.env.VUE_APP_BASE_API;
  }
  var xhr = new XMLHttpRequest();
  // xhr.open('GET', url, true);        // 使用GET方式比较简单，参数直接附在URL上
  xhr.open("post", url + urldata, true); //POST的格式相对比较灵活，参数可以有比较多的形式，例如JSON，表单FORM等
  xhr.responseType = "blob"; // 返回类型blob
  xhr.setRequestHeader("Content-Type", "application/json"); //提交的数据为json格式
  xhr.setRequestHeader("Authorization", that.getToken());
  // 定义请求完成的处理函数
  xhr.onload = function() {
    // 请求完成
    that.loading = false;
    if (this.status === 200) {
      // 返回200
      var blob = this.response;
      var reader = new FileReader();
      reader.readAsDataURL(blob); // 转换为base64，可以直接放入a表情href
      reader.onload = function(e) {
        // 转换完成，创建一个a标签用于下载
        var a = document.createElement("a");
        a.download = name + ".xls";
        a.href = e.target.result;
        $("body").append(a); // 修复firefox中无法触发click
        a.click();
        $(a).remove();
      };
    }
  };
  // 发送ajax请求,案例中我们使用POST的请求格式，参数类型为JSON
  xhr.send(JSON.stringify(data));
};
Tools.exportExcelGet = function(urldata, data, name, that) {
  let url;
  that.$modal.loading("正在导出数据，请稍后...");
  if (window.location.protocol == "http:") {
    // url = 'http://192.168.1.200:750/api';
    url = process.env.VUE_APP_BASE_API
  } else {
    url = process.env.VUE_APP_BASE_API;
  }
  var xhr = new XMLHttpRequest();
  // xhr.open('GET', url, true);        // 使用GET方式比较简单，参数直接附在URL上
  xhr.open("get", url + urldata, true); //POST的格式相对比较灵活，参数可以有比较多的形式，例如JSON，表单FORM等
  xhr.responseType = "blob"; // 返回类型blob
  xhr.setRequestHeader("Content-Type", "application/json"); //提交的数据为json格式
  xhr.setRequestHeader("Authorization", that.getToken());
  // 定义请求完成的处理函数
  xhr.onload = function() {
    // 请求完成
    
    if (this.status === 200) {
      that.openTemplate = false
      that.$modal.closeLoading();
      // 返回200
      var blob = this.response;
      var reader = new FileReader();
      reader.readAsDataURL(blob); // 转换为base64，可以直接放入a表情href
      reader.onload = function(e) {
        // 转换完成，创建一个a标签用于下载
        var a = document.createElement("a");
        a.download = name + ".xlsx";
        a.href = e.target.result;
        $("body").append(a); // 修复firefox中无法触发click
        a.click();
        $(a).remove();
      };
    }
  };
  // 发送ajax请求,案例中我们使用POST的请求格式，参数类型为JSON
  xhr.send(JSON.stringify(data));
}; 
module.exports = Tools;
