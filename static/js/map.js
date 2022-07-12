$(document).ready(function () {

    let map = new naver.maps.Map('map', {
        center: new naver.maps.LatLng(37.503072, 126.947753),
        zoom: 13,
        zoomControl: true,
        zoomControlOptions: {
            style: naver.maps.ZoomControlStyle.SMALL,
            position: naver.maps.Position.TOP_RIGHT
        }
    });

    let marker = new naver.maps.Marker({
        position: new naver.maps.LatLng(37.503072, 126.947753),
        map: map
    });

    let infowindow = new naver.maps.InfoWindow({
        content: `<div style="width: 50px;height: 20px;text-align: center"><h5>안녕!</h5></div>`,
    });
    naver.maps.Event.addListener(marker, "click", function () {
        console.log(infowindow.getMap()); // 정보창이 열려있을 때는 연결된 지도를 반환하고 닫혀있을 때는 null을 반환
        if (infowindow.getMap()) {
            infowindow.close();
        } else {
            infowindow.open(map, marker);
        }
    });
})