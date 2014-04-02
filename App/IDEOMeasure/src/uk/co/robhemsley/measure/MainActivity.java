package uk.co.robhemsley.measure;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import uk.co.robhemsley.utils.Debug;

import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.DialogInterface.OnDismissListener;
import android.content.Intent;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.View;
import android.view.Window;
import android.view.animation.AlphaAnimation;
import android.view.animation.Animation;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.AdapterView.OnItemLongClickListener;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

public class MainActivity extends Activity {
	/*
	 * MainActivity - Class
	 *  
	 * Starting activity used to display the previous measured materials and allow users
	 * to either add a new picture/material or inspect the previously calcualted details.
	 */
	
	
	private String TAG = Debug.getClassName();
	
    private static final int 	CAMERA_REQUEST 		= 1888; 										//The Intent request code
    public static final String 	MATERIAL_FILE 		= "uk.co.robhemsley.materialfile";				//The activity save state filename
    public static final String 	SOURCE 				= "uk.co.robhemsley.measure.source"; 			//The source from where the filename came from
    public static final String 	BASE_FILE 			= "uk.co.robhemsley.measure.basefile"; 			//The base filename 
    
    //Variables for the saved materials
    public static final String KEY_ID 				= "id";
    public static final String KEY_DATE 			= "date";
	public static final String KEY_TYPE 			= "type";
	public static final String KEY_DIMENSION 		= "dimension";
	public static final String KEY_THUMB_URL 		= "thumb_url";
	
    public String 				material_file_path;
    private Context 			mContext;
	
    //The listview controllers/loaders for images etc
	private ListView 			list;
	private LazyAdapter 		adapter;
	private TestDialog intro;

	@SuppressLint("NewApi")
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.home);
		mContext = this;
				
		/* So this needs some explaining... The android lifecycle means that the OS can put your app
		 * to sleep at anytime if it decides it wants the memory etc. In this we launch the camera
		 * App and ask to save the image to a specified location. The problem is once we launch the camera
		 * we sometimes find our app is closed and thus we lose the name of the file we told the camera to
		 * save to. To overcome this we save the filename to the app state.
		 */
		if (savedInstanceState != null){
			material_file_path = savedInstanceState.getString("filename");
		}
	
		//Add take image button and create anonymous action listener
		ImageButton scan = (ImageButton) findViewById(R.id.menu_plus_logo);
        scan.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
            	
            	//Create a location to save the file to
                material_file_path = Environment.getExternalStorageDirectory().getAbsolutePath();
                material_file_path += getResources().getString(R.string.file_save_dir)+UUID.randomUUID().toString()+".jpg";
                
                final File file_out = new File( material_file_path );
                
                //If dir doesn't exist then save it
                if(file_out.getParentFile().exists() == false){
                	file_out.getParentFile().mkdirs();
                }
                
                //Create a URI for the file
                Uri outputFileUri = Uri.fromFile( file_out );
                
                //Call the camera intent to take a photo to the specified location
                Intent cameraIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE); 
                cameraIntent.putExtra(MediaStore.EXTRA_OUTPUT, outputFileUri);
                startActivityForResult(cameraIntent, CAMERA_REQUEST); 
                overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left);
            }
        });


        
	    LayoutInflater inflater = this.getLayoutInflater();

	    final View welcome = inflater.inflate(R.layout.welcome, null);
        intro = new TestDialog(mContext, welcome);
        
        
        Button btn_start = (Button) welcome.findViewById(R.id.get_measuring);
        
        btn_start.setOnClickListener(new View.OnClickListener() 
        {

			@Override
			public void onClick(View v) {
					
				intro.dismiss();
				
				
            	//Create a location to save the file to
                material_file_path = Environment.getExternalStorageDirectory().getAbsolutePath();
                material_file_path += getResources().getString(R.string.file_save_dir)+UUID.randomUUID().toString()+".jpg";
                
                final File file_out = new File( material_file_path );
                
                //If dir doesn't exist then save it
                if(file_out.getParentFile().exists() == false){
                	file_out.getParentFile().mkdirs();
                }
                
                //Create a URI for the file
                Uri outputFileUri = Uri.fromFile( file_out );
                
                //Call the camera intent to take a photo to the specified location
                Intent cameraIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE); 
                cameraIntent.putExtra(MediaStore.EXTRA_OUTPUT, outputFileUri);
                startActivityForResult(cameraIntent, CAMERA_REQUEST); 
                overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left);
			}
            // Perform button logic
        });
        
        
        LinearLayout layout_test = (LinearLayout) welcome.findViewById(R.id.welcome_holder);
        

        layout_test.setOnClickListener(new View.OnClickListener() 
        {
            int screen_num = 0;

			@Override
			public void onClick(View v) {
				screen_num = screen_num + 1;

				if (screen_num < 4){
					intro.dismiss();
				}

			}
        });
        
        intro.setOnDismissListener(new OnDismissListener(){
            int screen_num = 0;

			@Override
			public void onDismiss(DialogInterface dialog) {
				final ImageView layer1 = (ImageView) intro.findViewById(R.id.welcome_img_layer1);
				final ImageView layer3 = (ImageView) intro.findViewById(R.id.welcome_img_layer3);
				final ImageView layer4 = (ImageView) intro.findViewById(R.id.welcome_img_layer4);
				final ImageView layer5 = (ImageView) intro.findViewById(R.id.welcome_img_layer5);
				final ImageView layer6 = (ImageView) intro.findViewById(R.id.welcome_img_layer6);

				final TextView title_text = (TextView) intro.findViewById(R.id.welcome_title_txt);
				final TextView des = (TextView) intro.findViewById(R.id.welcome_des_txt);



				screen_num = screen_num + 1;
				
				switch (screen_num) {
	            	case 1:
	            		title_text.setText("Copies");
	            		des.setText("Copies your physical objects");
	            		layer1.setImageResource(R.drawable.copy);
	    				intro.show();

	            		break;
	     
	            	case 2:
	            		title_text.setText("Digitises");
	            		des.setText("Creates accurate digital paths");

	            		layer1.setImageResource(R.drawable.digitise_1);
	    				intro.show();

	            		break;
	            		
	            	case 3:
	            		title_text.setText("Optimises");
	            		des.setText("Optimally positions for cutting");
	            		layer1.setImageResource(R.drawable.optimise_1);
						Button get_measuring = (Button) welcome.findViewById(R.id.get_measuring);
						get_measuring.setVisibility(Button.VISIBLE);
	    				intro.show();

	            		break;
				}
				
			}
        	
        	
        });
		
        //Load the listview with the saved material details
        populateList();

	}
	
	public void populateList(){
		//Create/Check the saved file directory on the SD card
		File dir = new File(Environment.getExternalStorageDirectory().getAbsolutePath()+getResources().getString(R.string.file_save_dir)+"Saved/");
        if(dir.exists() == false){
        	dir.mkdirs();
        }
        
		ArrayList<HashMap<String, String>> filesList = new ArrayList<HashMap<String, String>>();
        
		if (ListDir(dir).size() == 0){
			intro.show();
		}
		
		//Iterate over the directory structure for txt files
		for (String file :ListDir(dir)){
			if (file.contains(".txt")){
					
				try {
					//Read the txt file and it's contained JSON
					BufferedReader br = new BufferedReader(new FileReader(file));
					String line;
					String output = "";

					while ((line = br.readLine()) != null) {
						output += line+'\n';
					}
					
					JSONParser parser = new JSONParser();
            		
					Object obj = parser.parse(output);
                	JSONObject res_obj = (JSONObject) obj;
                	
            		JSONObject exterior = (JSONObject) res_obj.get("exterior");
            		String dimension = (String) exterior.get("width") + "mm X " + (String) exterior.get("height") + "mm";
            		
            		String time = (String) exterior.get("_timestamp");
            		String time_human = new java.text.SimpleDateFormat("MM/dd/yyyy HH:mm:ss").format(new java.util.Date ((long) (Double.parseDouble(time.trim().toString())*1000)));
            		
            		HashMap<String, String> map = new HashMap<String, String>();

            		String material_id = file.substring(file.lastIndexOf('/')+1, file.lastIndexOf('.'));
            		map.put(MainActivity.KEY_ID, material_id);
        			map.put(MainActivity.KEY_DATE, time_human);
        			map.put(MainActivity.KEY_DIMENSION, dimension);
        			map.put(MainActivity.KEY_TYPE, "Wood");
        			
        			String preview_img = file.substring(0, file.lastIndexOf('.'))+".jpg";
        			
        			map.put(KEY_THUMB_URL, preview_img);
        			//Add to map
        			filesList.add(map);

				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (ParseException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			
		}
		//Load files with the adapter
        adapter = new LazyAdapter(this, filesList);  
        
        //Setup the list
        list = (ListView)findViewById(R.id.list);
        list.setAdapter(adapter);
        
        //Add anonymous method for on click
        list.setOnItemClickListener(new OnItemClickListener(){

			@Override
			public void onItemClick(AdapterView<?> arg0, View view, int pos, long id) {
				//Move to main activity
        		String base = Environment.getExternalStorageDirectory().getAbsolutePath()+getResources().getString(R.string.file_save_dir)+"Saved/";

                HashMap<String, String> material = adapter.getData(pos);
                String base_files = base+material.get(KEY_ID);
				
	        	Intent i = new Intent(MainActivity.this, ViewMeasure.class);
	        	//Add the extra details to the intent indicating the app flow.
	        	i.putExtra(MATERIAL_FILE, material_file_path);
	        	i.putExtra(SOURCE, "app");
	        	i.putExtra(BASE_FILE, base_files);

	        	startActivity(i);
	            overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left);
			}
			
        });
        
        //Setup the delete option on a long press
        list.setOnItemLongClickListener(new OnItemLongClickListener(){

			@Override
			public boolean onItemLongClick(AdapterView<?> arg0, View view, final int pos, long id) {
				
				//Build a fake context menu
				final CharSequence[] items = {"Position", "Delete"};
				AlertDialog.Builder builder = new AlertDialog.Builder(mContext);

				builder.setItems(items, new DialogInterface.OnClickListener() {
				    public void onClick(DialogInterface dialog, int item) {
				    	if (item == 1){
			                HashMap<String, String> material = adapter.getData(pos);
			                String ID = material.get(KEY_ID);
			                
			                //Remove the tag from the list and force redraw
							adapter.removeItem(pos);
							adapter.notifyDataSetChanged();
			                list.invalidate();
			                
			                Log.i(TAG, "REMOVE ITEM:"+ID);
			                deleteMaterial(ID);
				    	}
				    }
				});
				AlertDialog alert = builder.create();
				alert.show();
				
				return false;
			}
        	
        });
		
	}
	
	public void deleteMaterial(String ID){
		//Takes the ID and then deletes all the contained elements associated with that file
		String base = Environment.getExternalStorageDirectory().getAbsolutePath()+getResources().getString(R.string.file_save_dir)+"Saved/";

		File dir = new File(base+ID+".txt");
		if(dir.exists()){
			dir.delete();
		}
		
		dir = new File(base+ID+".jpg");
		if(dir.exists()){
			dir.delete();
		}
		
		dir = new File(base+ID+"_outline.jpg");
		if(dir.exists()){
			dir.delete();
		}

	}

	public List<String> ListDir(File f){
		//Lists the contents of a specified directory
		File[] files = f.listFiles();
	    List<String> fileList = new ArrayList<String>();
	    for (File file : files){
	    	fileList.add(file.getPath()); 
	    }
	    return fileList;
	}
	

	protected void onActivityResult(int requestCode, int resultCode, Intent data) {  
		//When the intent for the camera has finished this method is called
		if (requestCode == CAMERA_REQUEST && resultCode == RESULT_OK) { 
			//Create and load a new intent
        	Intent i = new Intent(MainActivity.this, ViewMeasure.class);
        	i.putExtra(MainActivity.MATERIAL_FILE, material_file_path);
        	i.putExtra(MainActivity.SOURCE, "camera");

        	startActivity(i);
            overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left);
        }  
    } 
	
	
	protected void onSaveInstanceState(Bundle bundle) {
		//When the app is about to close due to the intent problem we save the filename
		//that the app previously requested.
		super.onSaveInstanceState(bundle);
		
		if(material_file_path != null){
			bundle.putString("filename", material_file_path);
		}
	}
}
