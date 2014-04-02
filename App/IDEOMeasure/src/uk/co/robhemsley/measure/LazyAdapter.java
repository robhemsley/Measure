package uk.co.robhemsley.measure;

import java.util.ArrayList;
import java.util.HashMap;

import android.app.Activity;
import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;

public class LazyAdapter extends BaseAdapter {
    
    private Activity 							activity;
    private ArrayList<HashMap<String, String>> 	data;
    private static LayoutInflater 				inflater = null;
    public ImageLoader 							imageLoader; 
    
    public LazyAdapter(Activity a, ArrayList<HashMap<String, String>> d) {
        activity = a;
        data = d;
        inflater = (LayoutInflater)activity.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        imageLoader = new ImageLoader(activity.getApplicationContext());
    }

    public int getCount() {
        return data.size();
    }

    public Object getItem(int position) {
        return position;
    }
    
    public HashMap<String, String> getData(int pos){
    	return this.data.get(pos);
    }

    public long getItemId(int position) {
        return position;
    }
    
    public void removeItem(int position){
    	this.data.remove(position);
    }
    
    public View getView(int position, View convertView, ViewGroup parent) {
        View vi=convertView;
        if(convertView==null)
            vi = inflater.inflate(R.layout.list_row, null);

        TextView date = (TextView)vi.findViewById(R.id.date); // Date
        TextView type = (TextView)vi.findViewById(R.id.type); // Type
        TextView dimensions = (TextView)vi.findViewById(R.id.dimensions); // Type
        uk.co.robhemsley.measure.ResizableImageView thumb_image=(uk.co.robhemsley.measure.ResizableImageView)vi.findViewById(R.id.list_image); // thumb image
        
        HashMap<String, String> song = new HashMap<String, String>();
        song = data.get(position);
        
        // Setting all values in listview
        date.setText(song.get(MainActivity.KEY_DATE));
        type.setText(song.get(MainActivity.KEY_TYPE));
        dimensions.setText(song.get(MainActivity.KEY_DIMENSION));

        imageLoader.DisplayImage(song.get(MainActivity.KEY_THUMB_URL), thumb_image);
        return vi;
    }
}