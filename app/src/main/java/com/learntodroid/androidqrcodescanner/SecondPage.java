package com.learntodroid.androidqrcodescanner;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.location.Location;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.android.volley.NetworkResponse;
import com.android.volley.toolbox.StringRequest;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.tasks.OnSuccessListener;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import org.json.JSONException;
import org.json.JSONObject;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import com.learntodroid.androidqrcodescanner.RetrieveFeedTask;

public class SecondPage extends AppCompatActivity {
    private FusedLocationProviderClient fusedLocationClient;

    String url;
        public static void GetData(JSONObject response,TextView Whether, String geopos, Button SendInfo,TextView Checkqr, RequestQueue requestQueue, String qr_code) {
        try {
            JSONObject data = response.getJSONObject("current");
            String temp_c = String.valueOf(data.getDouble("temp_c"));
            JSONObject condition = data.getJSONObject("condition");
            String pogoda = condition.getString("text");
            String wind_speed = String.valueOf(data.getDouble("wind_kph"));
            String wind_dir = data.getString("wind_dir");
            String pressure_mb = String.valueOf(data.getDouble("pressure_mb"));  // milli bar

            String result_for_device = "Температура: " + temp_c + ", \nСостояние: " + pogoda + ", \nСкорость ветра: " + wind_speed + ", \nНаправление ветра: " + wind_dir + ", \nДавление(миллибары): " + pressure_mb;
            Whether.setText(result_for_device);

            String result_for_server = temp_c + "&" + geopos;

            SendInfo.setOnClickListener(
                    new View.OnClickListener() {
                        @Override
                        public void onClick(View v) {

                            StringRequest Request_for_server = new StringRequest(Request.Method.GET, "http://62.109.17.249:1337/req/" + qr_code + "/" + result_for_server, new Response.Listener<String>() {
                                @Override
                                public void onResponse(String response) {                // Display the first 500 characters of the response string.
                                    Checkqr.setText("Response is: " + response);


                                }
                            }, new Response.ErrorListener() {
                                @Override
                                public void onErrorResponse(VolleyError error) {
                                    Checkqr.setText("That didn't work!");
                                }
                            });
                            requestQueue.add(Request_for_server);


                        }
                    }
            );

        } catch (JSONException e) {
            throw new RuntimeException(e);
        }
    }

    public static void Success(Location location,TextView GeoPos,TextView Whether, Button SendInfo,TextView Checkqr, RequestQueue requestQueue, String qr_code){
        // Got last known location. In some rare situations this can be null.
        if (location != null) {
            String geopos =  location.getLatitude() +"," + location.getLongitude();
            GeoPos.setText(geopos);


            String url = "https://api.weatherapi.com/v1/current.json?q="+location.getLatitude()+","+location.getLongitude()+"&key=d98e7c7729f14db6bae180859231312";

            JsonObjectRequest jsonArrayRequest = new JsonObjectRequest(
                    Request.Method.GET, url, null,
                    new Response.Listener<JSONObject>() {
                        @Override
                        public void onResponse(JSONObject response)
                        {
                            GetData(response,Whether,geopos,SendInfo,Checkqr,requestQueue,qr_code);

                        }
                    },
                    new Response.ErrorListener() {
                        @Override
                        public void onErrorResponse(VolleyError error)
                        {
                        }
                    });

            requestQueue.add(jsonArrayRequest);



        }}

        @SuppressLint("WrongThread")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_second_page);

        Button button=findViewById(R.id.SendPhoto);
        button.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        Intent intent=new Intent(SecondPage.this,Photo_activity.class);
                        startActivity(intent);

                    }
                }
        );


        Button SendInfo=findViewById(R.id.SendInfo);



        Bundle arguments = getIntent().getExtras();
        String qr_code = arguments.get("qr").toString();
        TextView Code = findViewById(R.id.Code);
        Code.setText(qr_code);

        Date currentTime = Calendar.getInstance().getTime();
        DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        String strDate = dateFormat.format(currentTime);

        TextView Data = findViewById(R.id.Data);
        Data.setText(strDate);

        TextView GeoPos = findViewById(R.id.GeoPos);
        GeoPos.setText("No coord");

        TextView Checkqr = findViewById(R.id.checkqr);


        TextView Whether = findViewById(R.id.whether);

        RequestQueue requestQueue = Volley.newRequestQueue(this);
        final int[] Check_qr_status = new int[1];
        String send_qr = "http://62.109.17.249:1337/req/"+qr_code+"/";
        NetworkResponseRequest request = new NetworkResponseRequest(Request.Method.GET, send_qr,
                new Response.Listener<NetworkResponse>() {
                    @Override
                    public void onResponse(NetworkResponse response) {
                        Check_qr_status[0] =response.statusCode;
                        //Checkqr.setText(String.valueOf(response.statusCode));
                        if(Check_qr_status[0]==202){
                            Checkqr.setText("Хороший код!:)");
                            if (ActivityCompat.checkSelfPermission(SecondPage.this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                                ActivityCompat.requestPermissions(SecondPage.this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, 1);
                            }
                            else {
                                fusedLocationClient = LocationServices.getFusedLocationProviderClient(SecondPage.this);
                                fusedLocationClient.getLastLocation()
                                        .addOnSuccessListener(SecondPage.this, new OnSuccessListener<Location>() {
                                            @Override
                                            public void onSuccess(Location location) {
                                                 Success(location,GeoPos,Whether,SendInfo,Checkqr,requestQueue,qr_code);
                                            }
                                        });
                            }}

                        else if(Check_qr_status[0]==410){
                            Checkqr.setText("использованный код!:(");

                        }
                        else if(Check_qr_status[0]==422){
                            Checkqr.setText("плохой код!:(");

                        }
                        else if(Check_qr_status[0]==406){
                            Checkqr.setText("исследование закончилось");

                        }
                        else if(Check_qr_status[0]==500){
                            Checkqr.setText("ошибка сервака");
                        }
                        else if(Check_qr_status[0]==666){
                            Checkqr.setText("Обновите приложение");
                        }
                        else{
                            Checkqr.setText(String.valueOf(Check_qr_status[0]));

                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {

                Checkqr.setText("Error");
            }
        }
        );
        requestQueue.add(request);


    }

}