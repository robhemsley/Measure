package uk.co.robhemsley.measure;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.util.Iterator;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import uk.co.robhemsley.utils.Debug;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.RequestParams;
import com.polites.android.GestureImageView;

import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.provider.MediaStore;
import android.annotation.SuppressLint;
import android.app.ActionBar.LayoutParams;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.View;
import android.view.Window;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TableLayout;
import android.widget.TextView;
import android.widget.Toast;

public class ViewMeasure extends Activity {
	/*
	 * ViewMeasure - Class
	 * 
	 * The second activity in the application. Responsible for displaying the actual size of the computed 
	 * material. If this is called via the camera intent then the image is downscaled and then saved to the
	 * SDcard before being pushed to the server where it is processed.
	 */
	
	private String 	TAG		 	= Debug.getClassName();
	private String 	file_loc 	= "";
	private Context mContext;
	private String 	data;
	private String 	svg_loc;
	private LayoutInflater inflater;
    
    final Handler uiHandler = new Handler(){
    	//As we don't want to block the UI thread but also wan't to update it we use
    	//this handler to interact between backgrounds threads and the UI thread. 
    	
    	@Override
	    public void handleMessage(Message msg) {
    		//Log.i(TAG, msg.obj.getClass().toString());
    		if (msg.obj instanceof Throwable == false){
        		updateUI((String)msg.obj, true);
        		
    		}else{
    			//When something goes wrong with the request to the webserver
    			//So when the user is offline/The server crashes/etc
    			//This is a horrible catchall - Should test the msg.obj type and branch from there
    			LinearLayout layout = (LinearLayout) findViewById(R.id.progress_layout);
    			layout.setVisibility(View.GONE);
    			
    			//Show the UI elements
    			layout = (LinearLayout) findViewById(R.id.error_layout);
    			TextView tv = (TextView) findViewById(R.id.error_msg_txt);
    			Button try_again = (Button) findViewById(R.id.try_again_button);
    			try_again.setVisibility(View.VISIBLE);
    			
    			//Set the 'Error' message to the default value
    			tv.setText(getResources().getString(R.string.catchall_err_msg));
    			layout.setVisibility(View.VISIBLE);
    		}
	    }
    };

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.measuring);
		this.mContext = this;
		
		this.inflater = (LayoutInflater) this.getSystemService(Context.LAYOUT_INFLATER_SERVICE);

		
		try{
			//Determine how this activity was actually launched and then set the local details
			//Either load from SDcard of from the server
			Intent extras = this.getIntent();
			if(extras.getStringExtra(MainActivity.SOURCE).equals("camera") == false){
				String tmp = extras.getStringExtra(MainActivity.BASE_FILE);
				loadFromFiles(tmp);
				
			}else{
				String tmp = extras.getStringExtra(MainActivity.MATERIAL_FILE);
				file_loc = tmp;
				loadFromCamera();
			}
			
		}catch(Exception e){
			Log.i("Error", "Could not get the intent filename"+e.toString());
		}
        
		//Add onclick listener for the menu logo item
		ImageButton logo_btn = (ImageButton) findViewById(R.id.menu_ideo_logo);
		logo_btn.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
            	
            	Intent i = new Intent(ViewMeasure.this, MainActivity.class);
            	startActivity(i);
            	finish();
            }
        });
		
		//The try again button action listener - Attempts to send the material to the server
		//in a background thread
		Button try_again_btn = (Button) findViewById(R.id.try_again_button);
		try_again_btn.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
            	//Hide UI and show the progress bar
    			LinearLayout layout = (LinearLayout) findViewById(R.id.error_layout);
    			layout.setVisibility(View.GONE);
    			
    			layout = (LinearLayout) findViewById(R.id.progress_layout);
    			layout.setVisibility(View.VISIBLE);
    			
    			//Create a new runnable thread and call the sendMaterial fucntion
    			(new Thread(new Runnable() {
    				
    				@Override
    				public void run() {
    					sendMaterial();
    					
    				}
    			})).start(); 
            }
		});
		
		//The send SVG button action listener
		ImageButton share_btn = (ImageButton) findViewById(R.id.upload_btn);
		share_btn.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
            	
            	//Check that the SVG file has been generated
            	if(svg_loc != null){
                    Intent sendIntent = new Intent();
                    sendIntent.setAction(Intent.ACTION_SEND);
                    sendIntent.putExtra(Intent.EXTRA_STREAM, Uri.fromFile(new File(svg_loc)));
                    sendIntent.setType("image/svg+xml");
                    startActivity(Intent.createChooser(sendIntent, "Send SVG Dimensions"));
            	}else{
    				Toast toast = Toast.makeText(mContext, "SVG image not ready..", Toast.LENGTH_SHORT);
    				toast.show();
            	}
            }
        });  
	}
	
	public void loadFromCamera(){
		//Attempts to load the contents of the display from the camera image
		//Check file exists and load 
		File imgFile = new  File(file_loc);
		if(imgFile.exists()){

		    Bitmap myBitmap = BitmapFactory.decodeFile(imgFile.getAbsolutePath());
            Bitmap downImage = scaleDown(myBitmap, 1000, false);


		    ImageView myImage = (ImageView) findViewById(R.id.material_preview);
		    myImage.setImageBitmap(downImage);
		    myImage.invalidate();
		}
		
		//Background load thread - Server comms
		(new Thread(new Runnable() {
			
			@Override
			public void run() {
				sendMaterial();
				
			}
		})).start(); 
	}
	
	public void loadFromFiles(String base_file){
		//Loads all the details from the SDcard
		Bitmap myBitmap = BitmapFactory.decodeFile(base_file+".jpg");
		
	    ImageView myImage = (ImageView) findViewById(R.id.material_preview);
	    myImage.setImageBitmap(myBitmap);
	    myImage.invalidate();

	    try {
			BufferedReader br = new BufferedReader(new FileReader(base_file+".txt"));
			String line;
			String output = "";

			while ((line = br.readLine()) != null) {
				output += line+'\n';
			}
			
			updateUI(output, false);
			
			Bitmap outlineBitmap = BitmapFactory.decodeFile(base_file+"_outline.jpg");
			
		    ImageView preview = (ImageView) findViewById(R.id.material_preview);
		    preview.setImageBitmap(outlineBitmap);
		    svg_loc = base_file+".svg";
		    
		    br.close();
			
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	@SuppressLint("NewApi")
	public void updateUI(String response, Boolean download_img){
		//Sets the UI visual elements by parsing the JSON fromt he server or SD card.
		JSONParser parser = new JSONParser();
		
		LinearLayout layout = (LinearLayout) findViewById(R.id.progress_layout);
		layout.setVisibility(View.GONE);

		try {
			Object obj = parser.parse(response);

			JSONObject res_obj = (JSONObject) obj;

			Log.i(TAG, response);
		
			if (res_obj.containsKey("ERROR")){
				String error_str = (String) res_obj.get("ERROR_MSG");
				Log.i("ERROR", error_str);
				
				layout = (LinearLayout) findViewById(R.id.error_layout);
				layout.setVisibility(View.VISIBLE);
				
			}else{
	    		JSONObject exterior = (JSONObject) res_obj.get("exterior");
	    		String outline_url = (String) exterior.get("_outline");
	    		String svg_url = (String) exterior.get("_svg");
	    		
	    		layout = (LinearLayout) findViewById(R.id.materialDetailsLayout);

    			Log.i(TAG, "Object:"+(String) exterior.get("width"));
    			Log.i(TAG, "Object:"+(String) exterior.get("height"));
    			Log.i(TAG, "Object:"+(String) exterior.get("area"));

    			layout.addView(this.buildDetails("Exterior Shape:", R.drawable.measure_type_black));
    			layout.addView(this.buildDetails("\tHoles: "+(String)exterior.get("holes"), R.drawable.measure_type_red));
    			layout.addView(this.buildDetails("\tWidth: "+(String)exterior.get("width")+" mm", R.drawable.measure_type_red));
    			layout.addView(this.buildDetails("\tHeight: "+(String)exterior.get("height")+" mm", R.drawable.measure_type_red));
    			layout.addView(this.buildDetails("\tArea: "+(String)exterior.get("area")+" mm"+getResources().getString(R.string.sqr), R.drawable.measure_type_red));
	    			    		
	    		JSONArray interiorArray = (JSONArray) res_obj.get("interior");
	    	
	    		for(int i = 0; i < interiorArray.size(); i++){
	    			JSONObject interior = (JSONObject) interiorArray.get(i);		
	    		
	    			Log.i(TAG, "Object:");

	    			layout.addView(this.buildDetails("Interior Shape ("+i+"):", R.drawable.measure_type_black));
	    			layout.addView(this.buildDetails("\tWidth: "+(String)interior.get("width")+" mm", R.drawable.measure_type_blue));
	    			layout.addView(this.buildDetails("\tHeight: "+(String)interior.get("height")+" mm", R.drawable.measure_type_blue));
	    			layout.addView(this.buildDetails("\tArea: "+(String)interior.get("area")+" mm"+getResources().getString(R.string.sqr), R.drawable.measure_type_blue));
	    		}
	    		
	    		//If set the app will attempt to download the contents to the SD card in background processes
	    		if(download_img == true){
	    			new DownloadImageTask((GestureImageView) findViewById(R.id.material_preview)).execute(outline_url);	
	    			new DownloadFile(file_loc.substring(0, file_loc.lastIndexOf('/')) + "/Saved/" + file_loc.substring(file_loc.lastIndexOf('/'), file_loc.lastIndexOf('.'))+".svg").execute(svg_url);
	    		}
	    	}
			
		} catch (ParseException e) {
			e.printStackTrace();
		}
	}
	
	private LinearLayout buildDetails(String text, int resid){
		LinearLayout int_info = (LinearLayout)inflater.inflate(R.layout.measure_list_element, null);               
		TextView int_details = (TextView)int_info.findViewById(R.id.measure_list_element_text); // Date
		int_details.setText(text);
        ImageView img = (ImageView)int_info.findViewById(R.id.measure_list_element_img); // Date
		img.setBackgroundResource(resid);

		android.widget.LinearLayout.LayoutParams int_llp = new LinearLayout.LayoutParams(LayoutParams.FILL_PARENT, LayoutParams.WRAP_CONTENT, 0f);
		int_llp.setMargins(0, 2, 0, 0);
		int_info.setLayoutParams(int_llp);

		return int_info;
	}
	

	public void saveMaterial(Bitmap outline){
		//Saves the material details to the SD card. 
		
		File tmp = new File(file_loc.substring(0, file_loc.lastIndexOf('/')) + "/Saved/" + file_loc.substring(file_loc.lastIndexOf('/'), file_loc.lastIndexOf('.'))+".txt");
		try {
			FileOutputStream fOut = new FileOutputStream(tmp);
			OutputStreamWriter myOutWriter = new OutputStreamWriter(fOut);
			myOutWriter.write(data);
			myOutWriter.close();
			fOut.close();
			
			File imgFile = new File(file_loc);
			
		    imgFile.renameTo(new File(file_loc.substring(0, file_loc.lastIndexOf('/')) + "/Saved/" + file_loc.substring(file_loc.lastIndexOf('/'), file_loc.length())));
		
			FileOutputStream out = new FileOutputStream(file_loc.substring(0, file_loc.lastIndexOf('/')) + "/Saved/" + file_loc.substring(file_loc.lastIndexOf('/'), file_loc.lastIndexOf('.'))+"_outline.jpg");
			outline.compress(Bitmap.CompressFormat.JPEG, 100, out);
			
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void sendMaterial(){
		File imgFile = new  File(file_loc);
		if(imgFile.exists()){
		    
		    File myFile = new File(file_loc);
        	//Downscale the image
            Bitmap realImage = BitmapFactory.decodeFile(myFile.getAbsolutePath());
            Bitmap downImage = scaleDown(realImage, 1000, false);
            
            try {
                FileOutputStream out = new FileOutputStream(file_loc);
                downImage.compress(Bitmap.CompressFormat.JPEG, 70, out);
            } catch (Exception e) {
                e.printStackTrace();
            }
            
            File myFile1 = new File(file_loc);

            //Create the call to the server posting the details 
            AsyncHttpClient clientCall = new AsyncHttpClient();
            RequestParams params = new RequestParams();
            try {
                params.put("measure_img", myFile1);
            } catch(FileNotFoundException e) {}
            
            clientCall.post(this.mContext.getString(R.string.SERVER_URL)+"/measure", params, new AsyncHttpResponseHandler() {
               
            	@Override
                public void onSuccess(String response) {
            		//Sucess and update the UI
                	data = response;
        			Message msg = uiHandler.obtainMessage();
        			msg.obj = response;
        			uiHandler.sendMessage(msg);
                }
                
                @Override
                public void onFailure(Throwable e) {
                	//Fail and update the UI
                    Log.e(TAG, "OnFailure!", e);
  
        			Message msg = uiHandler.obtainMessage();
        			msg.obj = e;
        			uiHandler.sendMessage(msg);
                }
                
                @Override
                public void onFailure(Throwable e, String response) {
                    Log.e(TAG, "OnFailure!", e);
                    
                	Message msg = uiHandler.obtainMessage();
        			msg.obj = e;
        			uiHandler.sendMessage(msg);
                }
            });
		}else{
			Toast toast = Toast.makeText(mContext, "Camera Failed To Return An Image!", Toast.LENGTH_SHORT);
			toast.show();
		}
	}
	
	public static Bitmap scaleDown(Bitmap realImage, float maxImageSize, boolean filter) {
		//Downscales the image
		float ratio = Math.min((float) maxImageSize / realImage.getWidth(), (float) maxImageSize / realImage.getHeight());
		int width = Math.round((float) ratio * realImage.getWidth());
		int height = Math.round((float) ratio * realImage.getHeight());
    
		Bitmap newBitmap = Bitmap.createScaledBitmap(realImage, width, height, filter);
		
		return newBitmap;
	}
	
	private class DownloadImageTask extends AsyncTask<String, Void, Bitmap> {
		//AsyncTask for downloading the image and updating the display.
		GestureImageView bmImage;

		public DownloadImageTask(GestureImageView bmImage) {
			this.bmImage = bmImage;
		}

		protected Bitmap doInBackground(String... urls) {
			String urldisplay = urls[0];
			Bitmap materialPic = null;
			try {
				InputStream in = new java.net.URL(urldisplay).openStream();
				materialPic = BitmapFactory.decodeStream(in);
			} catch (Exception e) {
				Log.e("Error", e.getMessage());
				e.printStackTrace();
			}
      
			saveMaterial(materialPic);
      
			return materialPic;
		}

		protected void onPostExecute(Bitmap result) {
			bmImage.setImageBitmap(result);
		}
	}

	private class DownloadFile extends AsyncTask<String, Void, InputStream> {
		  String filename;

		  public DownloadFile(String filename) {
		      this.filename = filename;
		  }

		  protected InputStream doInBackground(String... urls) {
		      String urldisplay = urls[0];
		      InputStream in = null;
		      try {
		        in = new java.net.URL(urldisplay).openStream();
		      } catch (Exception e) {
		          Log.e("Error", e.getMessage());
		          e.printStackTrace();
		      }
		      
            
		      try {
					FileOutputStream f = new FileOutputStream(new File(filename));
				    byte[] buffer = new byte[1024];
			        int len1 = 0;
			        while ( (len1 = in.read(buffer)) > 0 ) {
			        	f.write(buffer,0, len1);
			        }

			        f.close();
			        
					svg_loc = file_loc.substring(0, file_loc.lastIndexOf('/')) + "/Saved/" + file_loc.substring(file_loc.lastIndexOf('/'), file_loc.lastIndexOf('.'))+".svg";

				} catch (FileNotFoundException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
		      
		      return in;
		  }

		  protected void onPostExecute(InputStream result) {
		  }
	}
	
	public void onPause() {
	     super.onPause();
	     overridePendingTransition(R.anim.slide_in_left, R.anim.slide_out_right);
	}
}
